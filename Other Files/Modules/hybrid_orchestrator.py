"""Task-, memory-, throughput-, and thermal-aware sequential model fusion.

Pocket AI v15's regular compact ladder is 0.6B -> 0.8B -> 1.5B ->
1.7B. The bundled 135M models remain emergency fallbacks. Hybrid routes load
one GGUF at a time; their parameter counts are never added together.
"""
from __future__ import annotations

from typing import Dict, Iterable, List

MiB = 1024 ** 2
GiB = 1024 ** 3
MODULE_VERSION = 3

QUALITY_ORDER = [
    "emergency_fast", "emergency_quality", "fast", "quality",
    "smart", "ultra", "pro", "max",
]
REGULAR_ORDER = ["fast", "quality", "smart", "ultra", "pro", "max"]
EMERGENCY_ORDER = ["emergency_fast", "emergency_quality"]
QUALITY_SCORE = {
    "emergency_fast": 0.10, "emergency_quality": 0.16,
    "fast": 0.42, "quality": 0.52, "smart": 0.66, "ultra": 0.74,
    "pro": 0.86, "max": 0.96,
}
MODEL_ESTIMATED_BYTES = {
    "emergency_fast": 90 * MiB,
    "emergency_quality": 100 * MiB,
    "fast": 700 * MiB,
    "quality": 563 * MiB,
    "smart": 1_100 * MiB,
    "ultra": 1_150 * MiB,
    "pro": 2_650 * MiB,
    "max": 5_250 * MiB,
}
MODEL_MIN_TOTAL = {
    "emergency_fast": 1_200 * MiB,
    "emergency_quality": 1_700 * MiB,
    "fast": 2_800 * MiB,
    "quality": 3_300 * MiB,
    "smart": 4_500 * MiB,
    "ultra": 5_200 * MiB,
    "pro": 7_400 * MiB,
    "max": 11_500 * MiB,
}
MODEL_MIN_CPU = {
    "emergency_fast": 0, "emergency_quality": 12,
    "fast": 24, "quality": 30, "smart": 39, "ultra": 45,
    "pro": 62, "max": 78,
}
MODEL_WORKSPACE = {
    "emergency_fast": 130 * MiB, "emergency_quality": 150 * MiB,
    "fast": 230 * MiB, "quality": 270 * MiB,
    "smart": 320 * MiB, "ultra": 350 * MiB,
    "pro": 440 * MiB, "max": 600 * MiB,
}

HYBRID_ROUTE_LABELS = {
    ("emergency_quality", "fast"): "emergency-135M→0.6B",
    ("fast", "quality"): "0.6B→0.8B",
    ("quality", "smart"): "0.8B→1.5B",
    ("smart", "ultra"): "1.5B→1.7B",
    ("ultra", "pro"): "1.7B→4B",
    ("pro", "max"): "4B→8B",
}


def _installed_sizes(available_models: Iterable[str], model_sizes: Dict[str, int]) -> Dict[str, int]:
    return {
        name: max(int(model_sizes.get(name, 0) or 0), MODEL_ESTIMATED_BYTES.get(name, 256 * MiB))
        for name in available_models
    }


def _system_reserve(total_ram: int) -> int:
    total = max(0, int(total_ram))
    if total < 3 * GiB:
        return 300 * MiB
    if total < 5 * GiB:
        return 500 * MiB
    if total < 8 * GiB:
        return 700 * MiB
    if total < 12 * GiB:
        return 950 * MiB
    return 1_200 * MiB


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
        "cool": 1.08, "normal": 1.12, "warm": 1.22,
        "hot": 1.38, "critical": 1.55,
    }.get(thermal_level, 1.22)

    result: List[str] = []
    for name in QUALITY_ORDER:
        if name not in installed:
            continue
        required = int(sizes[name] * multiplier) + MODEL_WORKSPACE[name]
        if int(total_ram) < MODEL_MIN_TOTAL[name]:
            continue
        if usable < required or int(cpu_score) < MODEL_MIN_CPU[name]:
            continue
        result.append(name)

    if result:
        return result

    # Last-resort fallbacks remain available only when Android still has a
    # meaningful reserve. They are never preferred over a safe regular tier.
    if thermal_level not in {"critical", "emergency"} and usable >= 180 * MiB:
        for fallback in ("emergency_quality", "emergency_fast"):
            if fallback in installed and int(total_ram) >= MODEL_MIN_TOTAL[fallback]:
                return [fallback]
    return []


def _immediate_lower(strongest: str, safe: List[str]) -> str | None:
    """Choose the nearest lower installed tier for a coherent hybrid bridge."""
    if strongest not in QUALITY_ORDER:
        return None
    strongest_index = QUALITY_ORDER.index(strongest)
    lower = [name for name in safe if QUALITY_ORDER.index(name) < strongest_index]
    if not lower:
        return None
    return max(lower, key=QUALITY_ORDER.index)


def _hybrid_label(first: str, second: str) -> str:
    return HYBRID_ROUTE_LABELS.get((first, second), f"{first}→{second}")


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
            "hybrid_class": "none",
            "reason": "No installed model fits the current thermal and live-memory safety envelope.",
        }

    regular_safe = [name for name in safe if name in REGULAR_ORDER]
    emergency_safe = [name for name in safe if name in EMERGENCY_ORDER]
    strongest = safe[-1]
    lowest_regular = regular_safe[0] if regular_safe else None
    lowest_safe = lowest_regular or (emergency_safe[0] if emergency_safe else safe[0])
    partner = _immediate_lower(strongest, safe)
    mode = requested_mode
    task = str(task_profile.get("task", "general_question"))
    difficult_tasks = {"math", "coding", "comparison", "causal_explanation", "recommendation", "research"}
    difficult = float(complexity) >= 0.62 or task in difficult_tasks
    very_difficult = float(complexity) >= 0.80 or task in {"coding", "math", "comparison"}
    cool_enough = thermal_level in {"cool", "normal"}
    severe_pressure = int(pressure_score) >= 5 or thermal_level in {"hot", "critical", "emergency"}

    if requested_mode == "auto":
        if severe_pressure:
            mode = "speed"
        elif partner and difficult and cool_enough and int(pressure_score) <= 2:
            mode = "fusion"
        elif specialist_present and strongest in {"quality", "smart", "ultra", "pro", "max"}:
            mode = "expert"
        else:
            mode = "smart"

    verification = bool(
        strongest in {"quality", "smart", "ultra", "pro", "max"}
        and very_difficult and cool_enough and int(pressure_score) <= 1
    )

    base = {"safe_models": safe, "regular_safe_models": regular_safe}
    if mode == "off":
        return {**base, "mode": "off", "steps": [], "roles": [], "verification_pass": False,
                "hybrid_class": "none", "reason": "Hybrid mode disabled."}
    if mode == "speed":
        # A 135M tier is selected only when no regular 0.6B+ tier fits, or when
        # live pressure is severe enough to require an emergency downgrade.
        selected = lowest_safe
        if severe_pressure and emergency_safe:
            selected = emergency_safe[0]
        return {**base, "mode": "speed", "steps": [selected], "roles": ["answer"],
                "verification_pass": False, "hybrid_class": "single-tier",
                "reason": "Lowest sustainable regular tier selected; emergency fallback is used only under severe pressure or when no 0.6B+ tier fits."}
    if mode in {"smart", "quality", "expert"}:
        return {
            **base, "mode": mode, "steps": [strongest],
            "roles": ["expert_answer" if mode == "expert" else "answer"],
            "verification_pass": verification, "hybrid_class": "single-tier",
            "reason": "Strongest installed model that fits the live RAM, CPU, and thermal envelope.",
        }

    if mode in {"adaptive", "cascade", "consensus", "fusion"} and partner and thermal_level in {"cool", "normal", "warm"}:
        if mode == "adaptive" and not very_difficult:
            return {**base, "mode": "adaptive", "steps": [strongest], "roles": ["answer"],
                    "verification_pass": False, "hybrid_class": "single-tier",
                    "reason": "One strong pass is more efficient for this task."}
        roles = {
            "adaptive": ["draft", "verify"],
            "cascade": ["draft", "rewrite"],
            "consensus": ["independent", "judge"],
            "fusion": ["analyst", "synthesizer"],
        }[mode]
        label = _hybrid_label(partner, strongest)
        return {
            **base, "mode": mode, "steps": [partner, strongest], "roles": roles,
            "verification_pass": verification and mode in {"fusion", "cascade"},
            "hybrid_class": label,
            "reason": (
                f"Sequential {label} {mode}: {partner} runs first, unloads, then {strongest} runs. "
                "This is a workflow bridge, not an additive parameter count."
            ),
        }

    return {
        **base, "mode": "smart", "steps": [strongest], "roles": ["answer"],
        "verification_pass": verification, "hybrid_class": "single-tier",
        "reason": "The multi-model request was reduced to one strongest sustainable pass.",
    }
