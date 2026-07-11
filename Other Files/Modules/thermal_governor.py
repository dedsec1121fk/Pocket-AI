"""Sustained-performance thermal governor for local Android inference.

The governor never disables Android's own thermal protections. It reduces load
before sustained throttling becomes severe, while allowing short cool-device
bursts that use more of the available CPU.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from time import monotonic
from typing import Deque, Dict, Iterable, Tuple

MiB = 1024 ** 2
GiB = 1024 ** 3
MODULE_VERSION = 1

MODEL_CONTEXT_BYTES_PER_TOKEN = {
    "fast": 24 * 1024,
    "quality": 28 * 1024,
    "smart": 96 * 1024,
    "ultra": 176 * 1024,
    "pro": 360 * 1024,
    "max": 690 * 1024,
}

MODEL_FALLBACK_BYTES = {
    "fast": 90 * MiB,
    "quality": 100 * MiB,
    "smart": 720 * MiB,
    "ultra": 1_150 * MiB,
    "pro": 2_650 * MiB,
    "max": 5_250 * MiB,
}

_LEVEL_ORDER = {"cool": 0, "normal": 1, "warm": 2, "hot": 3, "critical": 4, "emergency": 5}


def _reading_groups(snapshot: dict) -> Tuple[float, float, float]:
    battery = 0.0
    skin = 0.0
    silicon = 0.0
    for row in snapshot.get("readings", []) if isinstance(snapshot, dict) else []:
        try:
            value = float(row.get("celsius", 0.0) or 0.0)
        except (TypeError, ValueError):
            continue
        name = f"{row.get('type', '')} {row.get('zone', '')}".casefold()
        if not (5.0 <= value <= 115.0):
            continue
        if "batt" in name:
            battery = max(battery, value)
        elif any(token in name for token in ("skin", "surface", "shell", "case", "quiet")):
            skin = max(skin, value)
        else:
            silicon = max(silicon, value)
    fallback = float(snapshot.get("maximum_celsius", 0.0) or 0.0) if isinstance(snapshot, dict) else 0.0
    if not any((battery, skin, silicon)) and fallback > 0:
        silicon = fallback
    return battery, skin, silicon


def thermal_metrics(snapshot: dict) -> Dict:
    battery, skin, silicon = _reading_groups(snapshot)
    level = "cool"
    reasons = []

    if battery >= 47.5 or skin >= 49.0 or silicon >= 88.0:
        level = "emergency"
    elif battery >= 45.0 or skin >= 46.5 or silicon >= 81.0:
        level = "critical"
    elif battery >= 42.0 or skin >= 43.5 or silicon >= 72.0:
        level = "hot"
    elif battery >= 39.0 or skin >= 40.5 or silicon >= 62.0:
        level = "warm"
    elif battery >= 35.0 or skin >= 36.0 or silicon >= 50.0:
        level = "normal"

    if battery:
        reasons.append(f"battery {battery:.1f}°C")
    if skin:
        reasons.append(f"skin {skin:.1f}°C")
    if silicon:
        reasons.append(f"SoC {silicon:.1f}°C")

    return {
        "level": level,
        "score": _LEVEL_ORDER[level],
        "battery_celsius": round(battery, 1),
        "skin_celsius": round(skin, 1),
        "silicon_celsius": round(silicon, 1),
        "display_celsius": round(max(battery, skin, silicon), 1),
        "reason": ", ".join(reasons) or "no reliable sensor",
    }


def estimate_working_set(model: str, model_bytes: int, context: int, batch: int = 32) -> int:
    weights = max(int(model_bytes or 0), MODEL_FALLBACK_BYTES.get(model, 256 * MiB))
    kv = max(32 * MiB, int(context) * MODEL_CONTEXT_BYTES_PER_TOKEN.get(model, 128 * 1024))
    compute = max(96 * MiB, min(640 * MiB, int(weights * 0.10) + int(batch) * 2 * MiB))
    return int(weights * 1.04) + kv + compute


@dataclass
class ThermalDecision:
    level: str
    abort: bool
    reason: str
    temperature_rise: float
    cooldown_seconds: float


class ThermalGovernor:
    """Tracks trend and converts live heat/RAM state into sustainable settings."""

    def __init__(self, history_size: int = 12) -> None:
        self.history: Deque[Tuple[float, float, str]] = deque(maxlen=max(4, history_size))

    def observe(self, snapshot: dict) -> Dict:
        metrics = thermal_metrics(snapshot)
        now = monotonic()
        self.history.append((now, float(metrics["display_celsius"]), str(metrics["level"])))
        recent = [(t, v) for t, v, _ in self.history if now - t <= 30.0 and v > 0]
        rise = 0.0
        if len(recent) >= 2:
            rise = recent[-1][1] - min(v for _, v in recent[:-1])
        metrics["rise_30s"] = round(rise, 1)
        if rise >= 5.0 and metrics["score"] < _LEVEL_ORDER["critical"]:
            metrics["score"] += 1
            metrics["level"] = next(name for name, score in _LEVEL_ORDER.items() if score == metrics["score"])
            metrics["reason"] += f", rising quickly (+{rise:.1f}°C/30s)"
        return metrics

    @staticmethod
    def reserve_bytes(total_ram: int, charging: bool = False) -> int:
        total = max(0, int(total_ram))
        if total < 3 * GiB:
            reserve = 280 * MiB
        elif total < 6 * GiB:
            reserve = 520 * MiB
        elif total < 10 * GiB:
            reserve = 850 * MiB
        else:
            reserve = 1_150 * MiB
        if charging:
            reserve += 64 * MiB
        return reserve

    def adjust_runtime(
        self,
        plan: dict,
        *,
        model: str,
        model_bytes: int,
        total_ram: int,
        available_ram: int,
        cores: int,
        cpu_score: int,
        thermal_snapshot: dict,
        charging: bool,
        battery_percent: int,
    ) -> Dict:
        result = dict(plan)
        metrics = self.observe(thermal_snapshot)
        level = str(metrics["level"])
        core_limit = max(1, min(6, max(1, int(cores) - 1)))
        cpu_score = max(0, min(100, int(cpu_score)))

        if level in {"cool", "normal"}:
            if cpu_score >= 78:
                result["threads"] = min(core_limit, max(int(result.get("threads", 1)), 6))
            elif cpu_score >= 58:
                result["threads"] = min(core_limit, max(int(result.get("threads", 1)), 4))
            elif cpu_score >= 36:
                result["threads"] = min(core_limit, max(int(result.get("threads", 1)), 3))
            result["batch"] = min(96, max(int(result.get("batch", 16)), int(result.get("batch", 16) * 1.20)))
            result["ubatch"] = min(int(result["batch"]), max(8, int(result.get("ubatch", 8))))
        elif level == "warm":
            result["threads"] = max(1, min(int(result.get("threads", 2)), 3))
            result["batch"] = min(int(result.get("batch", 32)), 40)
            result["ubatch"] = min(int(result.get("ubatch", 16)), 20)
            result["max_tokens"] = min(int(result.get("max_tokens", 128)), 256)
        elif level == "hot":
            result["threads"] = max(1, min(int(result.get("threads", 2)), 2))
            result["context"] = min(int(result.get("context", 512)), 1024)
            result["batch"] = min(int(result.get("batch", 24)), 24)
            result["ubatch"] = min(int(result.get("ubatch", 12)), 12)
            result["max_tokens"] = min(int(result.get("max_tokens", 96)), 144)
        elif level == "critical":
            result.update({"threads": 1, "context": min(int(result.get("context", 384)), 512),
                           "batch": 8, "ubatch": 8,
                           "max_tokens": min(int(result.get("max_tokens", 64)), 72)})
        else:
            result.update({"threads": 1, "context": 192, "batch": 8, "ubatch": 8,
                           "max_tokens": 32})

        # Charging at an already warm battery creates sustained heat faster.
        if charging and metrics["battery_celsius"] >= 39.0:
            result["threads"] = max(1, int(result["threads"]) - 1)
            result["batch"] = min(int(result["batch"]), 24)
        if battery_percent and battery_percent <= 10 and not charging:
            result["threads"] = 1
            result["max_tokens"] = min(int(result["max_tokens"]), 80)

        reserve = self.reserve_bytes(total_ram, charging)
        free_for_model = max(0, int(available_ram) - reserve)
        working_set = estimate_working_set(model, model_bytes, int(result["context"]), int(result["batch"]))
        while result["context"] > 192 and working_set > free_for_model:
            result["context"] = max(192, int(result["context"] * 0.75))
            result["batch"] = max(8, min(int(result["batch"]), int(result["context"] // 16)))
            result["ubatch"] = max(8, min(int(result["ubatch"]), int(result["batch"])))
            working_set = estimate_working_set(model, model_bytes, int(result["context"]), int(result["batch"]))

        unsafe_memory = working_set > free_for_model
        guards = list(result.get("guards", []))
        if level not in {"cool", "normal"}:
            guards.append(f"thermal governor: {level} ({metrics['reason']})")
        if unsafe_memory:
            guards.append("estimated model working set exceeds safe live-RAM budget")
        result.update({
            "thermal_level": level,
            "thermal_metrics": metrics,
            "estimated_working_set_bytes": working_set,
            "reserved_system_ram_bytes": reserve,
            "free_model_budget_bytes": free_for_model,
            "unsafe_memory": unsafe_memory,
            "abort_before_start": level == "emergency" or unsafe_memory,
            "monitor_interval_seconds": 2.0,
            "abort_temperature_rise_celsius": 8.0,
            "guards": list(dict.fromkeys(guards)),
        })
        return result

    def check_during_run(
        self,
        snapshot: dict,
        *,
        baseline_temperature: float,
        available_ram: int,
        minimum_free_ram: int,
    ) -> ThermalDecision:
        metrics = self.observe(snapshot)
        current = float(metrics["display_celsius"] or 0.0)
        rise = current - float(baseline_temperature or current)
        abort = False
        reason = ""
        if metrics["level"] == "emergency":
            abort = True
            reason = "emergency thermal level"
        elif metrics["level"] == "critical" and rise >= 4.0:
            abort = True
            reason = "critical temperature with a rapid rise"
        elif available_ram and available_ram < max(120 * MiB, int(minimum_free_ram)):
            abort = True
            reason = "critical free-RAM pressure"
        cooldown = 0.0
        if metrics["level"] == "warm":
            cooldown = 1.5
        elif metrics["level"] == "hot":
            cooldown = 4.0
        elif metrics["level"] in {"critical", "emergency"}:
            cooldown = 8.0
        return ThermalDecision(metrics["level"], abort, reason, round(rise, 1), cooldown)

    def cooldown_between_passes(self, before: dict, after: dict) -> float:
        first = thermal_metrics(before)
        second = self.observe(after)
        rise = float(second.get("display_celsius", 0.0)) - float(first.get("display_celsius", 0.0))
        if second["level"] in {"critical", "emergency"}:
            return 10.0
        if second["level"] == "hot" or rise >= 5.0:
            return 6.0
        if second["level"] == "warm" or rise >= 3.0:
            return 3.0
        return 0.0
