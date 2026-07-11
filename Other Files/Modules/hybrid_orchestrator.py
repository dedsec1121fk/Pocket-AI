"""Task-, memory-, throughput-, and thermal-aware sequential model fusion.

Models are never kept loaded together. The planner chooses the strongest safe
model and, only when conditions allow, a compact analyst followed by a stronger
synthesizer and an optional short final critic pass.
"""
from __future__ import annotations

from typing import Dict, Iterable, List

MiB = 1024 ** 2
GiB = 1024 ** 3
MODULE_VERSION = 2

QUALITY_ORDER = ["fast", "quality", "smart", "ultra", "pro", "max"]
QUALITY_SCORE = {"fast": 0.18, "quality": 0.25, "smart": 0.52, "ultra": 0.70, "pro": 0.85, "max": 0.95}
MODEL_ESTIMATED_BYTES = {
    "fast": 90 * MiB,
    "quality": 100 * MiB,
    "smart": 720 * MiB,
    "ultra": 1_150 * MiB,
    "pro": 2_650 * MiB,
    "max": 5_250 * MiB,
}
MODEL_MIN_TOTAL = {
    "fast": 1 * GiB,
    "quality": 1_700 * MiB,
    "smart": 3_000 * MiB,
    "ultra": 4_500 * MiB,
    "pro": 7_000 * MiB,
    "max": 11_500 * MiB,
}
MODEL_MIN_CPU = {"fast": 0, "quality": 16, "smart": 25, "ultra": 43, "pro": 62, "max": 78}


def _installed_sizes(available_models: Iterable[str], model_sizes: Dict[str, int]) -> Dict[str, int]:
    return {
        name: max(int(model_sizes.get(name, 0) or 0), MODEL_ESTIMATED_BYTES.get(name, 256 * MiB))
        for name in available_models
    }


def _system_reserve(total_ram: int) -> int:
    total = max(0, int(total_ram))
    if total < 3 * GiB:
        return 300 * MiB
    if total < 6 * GiB:
        return 550 * MiB
    if total < 10 * GiB:
        return 850 * MiB
    return 1_150 * MiB


def safe_models(
    available_models: Iterable[str],
    *,
    total_ram: int,
    available_ram: int,
    cpu_score: int,
    thermal_level: str,
    model_sizes: Dict[str, int],
) -> List[str]:
    installed = set(available_models)
    sizes = _installed_sizes(installed, model_sizes)
    if thermal_level == "emergency":
        return []

    reserve = _system_reserve(total_ram)
    usable = max(0, int(available_ram) - reserve)
    multiplier = {
        "cool": 1.08,
        "normal": 1.12,
        "warm": 1.22,
        "hot": 1.38,
        "critical": 1.55,
    }.get(thermal_level, 1.22)

    result: List[str] = []
    for name in QUALITY_ORDER:
        if name not in installed:
            continue
        # Weight file + KV/compute workspace. The thermal governor performs a
        # second, more exact live check before launching the process.
        workspace = 150 * MiB if name in {"fast", "quality"} else (260 * MiB if name in {"smart", "ultra"} else 420 * MiB)
        required = int(sizes[name] * multiplier) + workspace
        if int(total_ram) < MODEL_MIN_TOTAL[name] or usable < required or int(cpu_score) < MODEL_MIN_CPU[name]:
            continue
        result.append(name)

    if result:
        return result

    # A tiny bundled fallback is permitted only when a real Android reserve remains.
    if thermal_level not in {"critical", "emergency"} and usable >= 190 * MiB:
        for fallback in ("quality", "fast"):
            if fallback in installed and int(total_ram) >= MODEL_MIN_TOTAL[fallback]:
                return [fallback]
    return []


def _compact_partner(strongest: str, safe: List[str]) -> str | None:
    candidates = [name for name in safe if name != strongest and QUALITY_SCORE[name] < QUALITY_SCORE[strongest]]
    if not candidates:
        return None
    # Qwen 0.6B is a strong planner for larger Qwen tiers. For bundled-only
    # devices, Q2_K can still provide a short independent analysis for Q4_1.
    for preferred in ("smart", "ultra", "quality", "fast"):
        if preferred in candidates:
            return preferred
    return candidates[-1]


def build_hybrid_plan(
    *,
    requested_mode: str,
    available_models: Iterable[str],
    total_ram: int,
    available_ram: int,
    cpu_score: int,
    thermal_level: str,
    complexity: float,
    task_profile: dict,
    specialist_present: bool,
    model_sizes: Dict[str, int],
    pressure_score: int = 0,
) -> dict:
    safe = safe_models(
        available_models,
        total_ram=total_ram,
        available_ram=available_ram,
        cpu_score=cpu_score,
        thermal_level=thermal_level,
        model_sizes=model_sizes,
    )
    if not safe:
        return {
            "mode": "off", "steps": [], "roles": [], "verification_pass": False,
            "reason": "No installed model fits the current thermal and live-memory safety envelope.",
        }

    strongest = safe[-1]
    fastest = safe[0]
    partner = _compact_partner(strongest, safe)
    mode = requested_mode
    task = str(task_profile.get("task", "general_question"))
    difficult_tasks = {"math", "coding", "comparison", "causal_explanation", "recommendation", "research"}
    difficult = float(complexity) >= 0.62 or task in difficult_tasks
    very_difficult = float(complexity) >= 0.80 or task in {"coding", "math", "comparison"}
    cool_enough = thermal_level in {"cool", "normal"}

    if requested_mode == "auto":
        if int(pressure_score) >= 5 or thermal_level in {"hot", "critical", "emergency"}:
            mode = "speed"
        elif partner and difficult and cool_enough and int(pressure_score) <= 2:
            mode = "fusion"
        elif specialist_present and strongest in {"smart", "ultra", "pro", "max"}:
            mode = "expert"
        else:
            mode = "smart"

    verification = bool(
        strongest in {"smart", "ultra", "pro", "max"}
        and very_difficult
        and cool_enough
        and int(pressure_score) <= 1
    )

    if mode == "off":
        return {"mode": "off", "steps": [], "roles": [], "verification_pass": False, "safe_models": safe,
                "reason": "Hybrid mode disabled."}
    if mode == "speed":
        return {"mode": "speed", "steps": [fastest], "roles": ["answer"], "verification_pass": False,
                "safe_models": safe, "reason": "Lowest sustainable model selected for live pressure or heat."}
    if mode in {"smart", "quality", "expert"}:
        return {
            "mode": mode,
            "steps": [strongest],
            "roles": ["expert_answer" if mode == "expert" else "answer"],
            "verification_pass": verification,
            "safe_models": safe,
            "reason": "Strongest installed model that fits the live RAM, CPU, and thermal envelope.",
        }

    if mode in {"adaptive", "cascade", "consensus", "fusion"} and partner and thermal_level in {"cool", "normal", "warm"}:
        if mode == "adaptive" and not very_difficult:
            return {"mode": "adaptive", "steps": [strongest], "roles": ["answer"],
                    "verification_pass": False, "safe_models": safe,
                    "reason": "One strong pass is more efficient for this task."}
        roles = {
            "adaptive": ["draft", "verify"],
            "cascade": ["draft", "rewrite"],
            "consensus": ["independent", "judge"],
            "fusion": ["analyst", "synthesizer"],
        }[mode]
        return {
            "mode": mode,
            "steps": [partner, strongest],
            "roles": roles,
            "verification_pass": verification and mode in {"fusion", "cascade"},
            "safe_models": safe,
            "reason": f"Sequential {mode} uses {partner} then {strongest}; only one GGUF process is loaded at a time.",
        }

    return {
        "mode": "smart", "steps": [strongest], "roles": ["answer"],
        "verification_pass": verification, "safe_models": safe,
        "reason": "The multi-model request was reduced to one strongest sustainable pass.",
    }
