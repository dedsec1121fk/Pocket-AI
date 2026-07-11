"""Resource-aware sequential model fusion for Pocket AI v16.

The normal extended ladder is 0.6B -> 0.8B -> 1.5B -> 1.7B -> 2B -> 3B.
The bundled 135M models remain emergency fallbacks. Only one GGUF model is
resident at a time and hybrid parameter counts are never added together.
"""
from __future__ import annotations
from typing import Dict, Iterable, List

MiB = 1024 ** 2
GiB = 1024 ** 3
MODULE_VERSION = 4

QUALITY_ORDER = [
    "emergency_fast", "emergency_quality", "fast", "quality", "smart",
    "ultra", "advanced", "prime", "pro", "max",
]
REGULAR_ORDER = ["fast", "quality", "smart", "ultra", "advanced", "prime", "pro", "max"]
EMERGENCY_ORDER = ["emergency_fast", "emergency_quality"]
QUALITY_SCORE = {
    "emergency_fast": 0.10, "emergency_quality": 0.16,
    "fast": 0.42, "quality": 0.52, "smart": 0.66, "ultra": 0.74,
    "advanced": 0.80, "prime": 0.85, "pro": 0.89, "max": 0.96,
}
MODEL_ESTIMATED_BYTES = {
    "emergency_fast": 90 * MiB, "emergency_quality": 100 * MiB,
    "fast": 700 * MiB, "quality": 563 * MiB, "smart": 1100 * MiB,
    "ultra": 1150 * MiB, "advanced": 1300 * MiB, "prime": 2100 * MiB,
    "pro": 2650 * MiB, "max": 5250 * MiB,
}
MODEL_MIN_TOTAL = {
    "emergency_fast": 1200 * MiB, "emergency_quality": 1700 * MiB,
    "fast": 2800 * MiB, "quality": 3300 * MiB, "smart": 4500 * MiB,
    "ultra": 5200 * MiB, "advanced": 5800 * MiB, "prime": 6800 * MiB,
    "pro": 8600 * MiB, "max": 11500 * MiB,
}
MODEL_MIN_CPU = {
    "emergency_fast": 0, "emergency_quality": 12, "fast": 24, "quality": 30,
    "smart": 39, "ultra": 45, "advanced": 50, "prime": 58, "pro": 68, "max": 82,
}
MODEL_WORKSPACE = {
    "emergency_fast": 130 * MiB, "emergency_quality": 150 * MiB,
    "fast": 230 * MiB, "quality": 270 * MiB, "smart": 320 * MiB,
    "ultra": 350 * MiB, "advanced": 390 * MiB, "prime": 440 * MiB,
    "pro": 500 * MiB, "max": 650 * MiB,
}
HYBRID_ROUTE_LABELS = {
    ("emergency_quality", "fast"): "emergency-135M→0.6B",
    ("fast", "quality"): "0.6B→0.8B",
    ("quality", "smart"): "0.8B→1.5B",
    ("smart", "ultra"): "1.5B→1.7B",
    ("ultra", "advanced"): "1.7B→2B",
    ("advanced", "prime"): "2B→3B",
    ("prime", "pro"): "3B→4B",
    ("pro", "max"): "4B→8B",
}

def _installed_sizes(available_models: Iterable[str], model_sizes: Dict[str, int]) -> Dict[str, int]:
    return {name: max(int(model_sizes.get(name, 0) or 0), MODEL_ESTIMATED_BYTES.get(name, 256 * MiB)) for name in available_models}

def _system_reserve(total_ram: int) -> int:
    total = max(0, int(total_ram))
    if total < 3 * GiB: return 300 * MiB
    if total < 5 * GiB: return 500 * MiB
    if total < 8 * GiB: return 700 * MiB
    if total < 12 * GiB: return 950 * MiB
    return 1200 * MiB

def safe_models(available_models: Iterable[str], *, total_ram: int, available_ram: int,
                cpu_score: int, thermal_level: str, model_sizes: Dict[str, int]) -> List[str]:
    installed=set(available_models); sizes=_installed_sizes(installed,model_sizes)
    if thermal_level == "emergency": return []
    usable=max(0,int(available_ram)-_system_reserve(total_ram))
    multiplier={"cool":1.08,"normal":1.12,"warm":1.22,"hot":1.38,"critical":1.55}.get(thermal_level,1.22)
    result=[]
    for name in QUALITY_ORDER:
        if name not in installed: continue
        required=int(sizes[name]*multiplier)+MODEL_WORKSPACE[name]
        if int(total_ram)<MODEL_MIN_TOTAL[name] or usable<required or int(cpu_score)<MODEL_MIN_CPU[name]: continue
        result.append(name)
    if result: return result
    if thermal_level not in {"critical","emergency"} and usable>=180*MiB:
        for fallback in ("emergency_quality","emergency_fast"):
            if fallback in installed and int(total_ram)>=MODEL_MIN_TOTAL[fallback]: return [fallback]
    return []

def _immediate_lower(strongest: str, safe: List[str]) -> str | None:
    if strongest not in QUALITY_ORDER: return None
    idx=QUALITY_ORDER.index(strongest)
    lower=[name for name in safe if QUALITY_ORDER.index(name)<idx]
    return max(lower,key=QUALITY_ORDER.index) if lower else None

def _hybrid_label(first: str, second: str) -> str:
    return HYBRID_ROUTE_LABELS.get((first,second),f"{first}→{second}")

def build_hybrid_plan(*, requested_mode: str, available_models: Iterable[str], total_ram: int,
                      available_ram: int, cpu_score: int, thermal_level: str, complexity: float,
                      task_profile: dict, specialist_present: bool, model_sizes: Dict[str,int],
                      pressure_score: int=0) -> dict:
    safe=safe_models(available_models,total_ram=total_ram,available_ram=available_ram,
                     cpu_score=cpu_score,thermal_level=thermal_level,model_sizes=model_sizes)
    if not safe:
        return {"mode":"off","steps":[],"roles":[],"verification_pass":False,"hybrid_class":"none",
                "reason":"No installed model fits the current thermal and live-memory safety envelope."}
    regular=[n for n in safe if n in REGULAR_ORDER]; emergency=[n for n in safe if n in EMERGENCY_ORDER]
    strongest=safe[-1]; lowest_regular=regular[0] if regular else None
    lowest_safe=lowest_regular or (emergency[0] if emergency else safe[0]); partner=_immediate_lower(strongest,safe)
    mode=requested_mode; task=str(task_profile.get("task","general_question"))
    difficult=float(complexity)>=0.62 or task in {"math","coding","comparison","causal_explanation","recommendation","research"}
    very_difficult=float(complexity)>=0.80 or task in {"coding","math","comparison"}
    cool=thermal_level in {"cool","normal"}; severe=int(pressure_score)>=5 or thermal_level in {"hot","critical","emergency"}
    if requested_mode=="auto":
        if severe: mode="speed"
        elif partner and difficult and cool and int(pressure_score)<=2: mode="fusion"
        elif specialist_present and strongest in {"quality","smart","ultra","advanced","prime","pro","max"}: mode="expert"
        else: mode="smart"
    verification=bool(strongest in {"quality","smart","ultra","advanced","prime","pro","max"} and very_difficult and cool and int(pressure_score)<=1)
    base={"safe_models":safe,"regular_safe_models":regular}
    if mode=="off": return {**base,"mode":"off","steps":[],"roles":[],"verification_pass":False,"hybrid_class":"none","reason":"Hybrid mode disabled."}
    if mode=="speed":
        selected=emergency[0] if severe and emergency else lowest_safe
        return {**base,"mode":"speed","steps":[selected],"roles":["answer"],"verification_pass":False,"hybrid_class":"single-tier",
                "reason":"Lowest sustainable regular tier selected; 135M is reserved for severe pressure or no safe 0.6B+ tier."}
    if mode in {"smart","quality","expert"}:
        return {**base,"mode":mode,"steps":[strongest],"roles":["expert_answer" if mode=="expert" else "answer"],
                "verification_pass":verification,"hybrid_class":"single-tier",
                "reason":"Strongest installed model that fits live RAM, CPU, storage, deadline, and thermal limits."}
    if mode in {"adaptive","cascade","consensus","fusion"} and partner and thermal_level in {"cool","normal","warm"}:
        if mode=="adaptive" and not very_difficult:
            return {**base,"mode":"adaptive","steps":[strongest],"roles":["answer"],"verification_pass":False,"hybrid_class":"single-tier","reason":"One strong pass is more efficient for this task."}
        roles={"adaptive":["draft","verify"],"cascade":["draft","rewrite"],"consensus":["independent","judge"],"fusion":["analyst","synthesizer"]}[mode]
        label=_hybrid_label(partner,strongest)
        return {**base,"mode":mode,"steps":[partner,strongest],"roles":roles,
                "verification_pass":verification and mode in {"fusion","cascade"},"hybrid_class":label,
                "reason":f"Sequential {label} {mode}: {partner} runs, unloads, then {strongest} runs. Parameter counts are not additive."}
    return {**base,"mode":"smart","steps":[strongest],"roles":["answer"],"verification_pass":verification,
            "hybrid_class":"single-tier","reason":"The multi-model request was reduced to one strongest sustainable pass."}
