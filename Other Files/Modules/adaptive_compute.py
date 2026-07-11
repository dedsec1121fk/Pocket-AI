"""Persistent, safety-bounded performance learning for local GGUF inference.

This module learns how fast each installed model runs on the current phone and
uses that history to spend the answer deadline intelligently. It never bypasses
Android thermal limits and never overrides a thermal or RAM abort decision.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from time import time
from typing import Dict

MiB = 1024 ** 2
MODULE_VERSION = 1


def _ema(old: float, new: float, alpha: float = 0.25) -> float:
    return float(new) if old <= 0 else (1.0 - alpha) * float(old) + alpha * float(new)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class AdaptiveComputeController:
    """Learns a sustainable performance envelope from completed local runs."""

    def __init__(self, data_dir: Path) -> None:
        self.path = Path(data_dir) / "runtime_telemetry.json"
        self.data: Dict = {"version": MODULE_VERSION, "models": {}, "updated_at": 0}
        self._load()

    def _load(self) -> None:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and isinstance(payload.get("models"), dict):
                self.data = payload
        except (OSError, ValueError, TypeError):
            return

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = dict(self.data)
        payload["version"] = MODULE_VERSION
        payload["updated_at"] = int(time())
        handle = None
        try:
            handle = tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", delete=False,
                dir=str(self.path.parent), prefix=".runtime_telemetry.", suffix=".tmp",
            )
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
            handle.close()
            os.replace(handle.name, self.path)
        except OSError:
            try:
                if handle is not None and not handle.closed:
                    handle.close()
                if handle is not None:
                    Path(handle.name).unlink(missing_ok=True)
            except OSError:
                pass

    def model_stats(self, model: str) -> Dict:
        row = self.data.setdefault("models", {}).get(model, {})
        return dict(row) if isinstance(row, dict) else {}

    def tune_plan(
        self,
        plan: dict,
        *,
        model: str,
        max_context: int,
        max_tokens: int,
        available_ram: int,
        cores: int,
        cpu_score: int,
        thermal_metrics: dict,
        charging: bool,
        battery_percent: int,
        deadline_seconds: float,
    ) -> dict:
        """Use observed throughput and heat response without crossing hard guards."""
        result = dict(plan)
        if result.get("abort_before_start") or result.get("unsafe_memory"):
            return result

        level = str(thermal_metrics.get("level", "normal"))
        rise = float(thermal_metrics.get("rise_30s", 0.0) or 0.0)
        battery_c = float(thermal_metrics.get("battery_celsius", 0.0) or 0.0)
        stats = self.model_stats(model)
        runs = int(stats.get("runs", 0) or 0)
        abort_rate = float(stats.get("abort_rate", 0.0) or 0.0)
        heat_rise = float(stats.get("temperature_rise_ema", 0.0) or 0.0)
        chars_per_second = float(stats.get("chars_per_second_ema", 0.0) or 0.0)

        core_limit = max(1, min(6, int(cores) - 1 if int(cores) > 1 else 1))
        stable_cool = (
            level in {"cool", "normal"}
            and rise <= 1.8
            and heat_rise <= 3.0
            and abort_rate < 0.12
            and (not charging or battery_c < 38.5)
            and int(battery_percent or 100) > 12
        )
        conservative = level in {"warm", "hot", "critical", "emergency"} or abort_rate >= 0.20 or heat_rise >= 4.0

        if stable_cool:
            # Spend additional headroom on context and synthesis, not blindly on
            # every CPU core. This tends to improve answer quality while leaving
            # one core and a substantial RAM reserve for Android.
            if int(cpu_score) >= 72:
                result["threads"] = min(core_limit, max(int(result.get("threads", 1)), 5))
            elif int(cpu_score) >= 50:
                result["threads"] = min(core_limit, max(int(result.get("threads", 1)), 4))
            result["context"] = min(int(max_context), max(int(result.get("context", 512)), int(result.get("context", 512) * 1.22)))
            result["batch"] = min(112, max(int(result.get("batch", 16)), int(result.get("batch", 16) * 1.18)))
            result["ubatch"] = min(int(result["batch"]), max(int(result.get("ubatch", 8)), int(result.get("ubatch", 8) * 1.12)))
            result["max_tokens"] = min(int(max_tokens), max(int(result.get("max_tokens", 96)), int(result.get("max_tokens", 96) * 1.15)))
            result["adaptive_burst"] = True
        else:
            result["adaptive_burst"] = False

        if conservative:
            result["threads"] = max(1, min(int(result.get("threads", 1)), 3 if level == "warm" else 2))
            result["batch"] = max(8, min(int(result.get("batch", 16)), 32))
            result["ubatch"] = max(8, min(int(result.get("ubatch", 8)), int(result["batch"])))
            result["max_tokens"] = max(48, min(int(result.get("max_tokens", 96)), 192))

        # Use measured output speed to avoid requesting more text than can finish
        # inside the shared deadline. Four characters per generated token is a
        # conservative language-agnostic approximation for English and Greek.
        if runs >= 2 and chars_per_second > 1.0:
            usable_seconds = max(8.0, float(deadline_seconds) * (0.78 if stable_cool else 0.68))
            learned_token_limit = int(chars_per_second * usable_seconds / 4.0)
            result["max_tokens"] = max(48, min(int(result["max_tokens"]), int(max_tokens), learned_token_limit))
            result["learned_chars_per_second"] = round(chars_per_second, 2)

        # Never spend the RAM reserve established by the thermal governor.
        free_budget = int(result.get("free_model_budget_bytes", 0) or 0)
        working_set = int(result.get("estimated_working_set_bytes", 0) or 0)
        if free_budget and working_set and working_set > int(free_budget * 0.90):
            result["context"] = max(192, int(result["context"] * 0.82))
            result["batch"] = max(8, int(result["batch"] * 0.75))
            result["ubatch"] = min(int(result["ubatch"]), int(result["batch"]))
            result["adaptive_burst"] = False

        result["context"] = max(128, min(int(max_context), int(result["context"])))
        result["max_tokens"] = max(32, min(int(max_tokens), int(result["max_tokens"])))
        result["threads"] = max(1, min(core_limit, int(result["threads"])))
        result["adaptive_controller"] = {
            "runs": runs,
            "stable_cool": stable_cool,
            "historical_abort_rate": round(abort_rate, 3),
            "historical_temperature_rise": round(heat_rise, 2),
        }
        return result

    def record_run(
        self,
        *,
        model: str,
        elapsed_seconds: float,
        output_characters: int,
        temperature_rise: float,
        thermal_level: str,
        aborted: bool,
        threads: int,
        context: int,
        batch: int,
    ) -> Dict:
        models = self.data.setdefault("models", {})
        row = models.setdefault(model, {})
        runs = int(row.get("runs", 0) or 0) + 1
        completed = int(row.get("completed", 0) or 0) + (0 if aborted else 1)
        aborts = int(row.get("aborts", 0) or 0) + (1 if aborted else 0)
        elapsed = max(0.001, float(elapsed_seconds))
        cps = max(0.0, int(output_characters) / elapsed)
        row.update({
            "runs": runs,
            "completed": completed,
            "aborts": aborts,
            "abort_rate": aborts / max(1, runs),
            "chars_per_second_ema": _ema(float(row.get("chars_per_second_ema", 0.0) or 0.0), cps),
            "elapsed_seconds_ema": _ema(float(row.get("elapsed_seconds_ema", 0.0) or 0.0), elapsed),
            "temperature_rise_ema": _ema(float(row.get("temperature_rise_ema", 0.0) or 0.0), max(0.0, float(temperature_rise))),
            "last_thermal_level": str(thermal_level),
            "last_threads": int(threads),
            "last_context": int(context),
            "last_batch": int(batch),
            "last_output_characters": int(output_characters),
            "last_run_at": int(time()),
        })
        self._save()
        return dict(row)

    def summary(self) -> Dict:
        return {name: dict(row) for name, row in self.data.get("models", {}).items() if isinstance(row, dict)}
