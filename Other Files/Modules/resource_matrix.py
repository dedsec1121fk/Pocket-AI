"""Continuous Android CPU/RAM/storage runtime optimizer for Pocket AI.

The coarse matrix chooses a useful starting point. The separate thermal governor
then adjusts it from live battery/skin/SoC sensors before and during inference.
"""
from __future__ import annotations
from typing import Dict

MODULE_VERSION = 7
MiB = 1024 ** 2
GiB = 1024 ** 3

COMBINATION_TIERS = [
    {"id": "internal_critical", "min_ram": 0, "min_free": 0, "min_cpu": 0, "model": "internal", "profile": "ultra_eco"},
    {"id": "legacy_1gb", "min_ram": 512 * MiB, "min_free": 90 * MiB, "min_cpu": 0, "model": "internal", "profile": "ultra_eco"},
    {"id": "fast_2gb", "min_ram": 1450 * MiB, "min_free": 280 * MiB, "min_cpu": 12, "model": "fast", "profile": "eco"},
    {"id": "quality_2gb", "min_ram": 2050 * MiB, "min_free": 500 * MiB, "min_cpu": 22, "model": "quality", "profile": "entry"},
    {"id": "smart_4gb", "min_ram": 3300 * MiB, "min_free": 950 * MiB, "min_cpu": 27, "model": "smart", "profile": "balanced"},
    {"id": "smart_6gb", "min_ram": 5200 * MiB, "min_free": 1900 * MiB, "min_cpu": 55, "model": "smart", "profile": "performance"},
    {"id": "ultra_6gb", "min_ram": 5000 * MiB, "min_free": 1600 * MiB, "min_cpu": 47, "model": "ultra", "profile": "balanced"},
    {"id": "ultra_8gb", "min_ram": 7200 * MiB, "min_free": 2800 * MiB, "min_cpu": 68, "model": "ultra", "profile": "performance"},
    {"id": "pro_8gb", "min_ram": 7500 * MiB, "min_free": 3300 * MiB, "min_cpu": 66, "model": "pro", "profile": "performance"},
    {"id": "pro_12gb", "min_ram": 11000 * MiB, "min_free": 5200 * MiB, "min_cpu": 80, "model": "pro", "profile": "flagship"},
    {"id": "max_12gb", "min_ram": 12000 * MiB, "min_free": 6300 * MiB, "min_cpu": 82, "model": "max", "profile": "performance"},
    {"id": "max_16gb", "min_ram": 15000 * MiB, "min_free": 8200 * MiB, "min_cpu": 88, "model": "max", "profile": "flagship"},
]


def _coarse(total: int, available: int, cpu: int, is64: bool, temp: float) -> str:
    if (not is64) or total < 1450 * MiB or available < 230 * MiB:
        return "ultra_eco"
    if total < 2200 * MiB or available < 420 * MiB or cpu < 18:
        return "eco"
    if total < 3400 * MiB or available < 850 * MiB or cpu < 34:
        return "entry"
    if total < 6500 * MiB or available < 1700 * MiB or cpu < 66:
        return "balanced"
    if total >= 9000 * MiB and available >= 3800 * MiB and cpu >= 78:
        return "flagship"
    return "performance"


def _base_profile(profile: str, cores: int) -> tuple[int, int, int, int, int, int]:
    spare_core_limit = max(1, min(6, cores - 1 if cores > 1 else 1))
    if profile == "ultra_eco":
        return 320, 8, 8, 64, 1, 106
    if profile == "eco":
        return 512, 16, 8, 96, 1, 106
    if profile == "entry":
        return 896, 32, 16, 168, min(2, spare_core_limit), 104
    if profile == "balanced":
        return 1536, 64, 32, 288, min(4, spare_core_limit), 102
    if profile == "flagship":
        return 3584, 112, 56, 640, spare_core_limit, 98
    return 2560, 96, 48, 448, spare_core_limit, 100


def optimize_runtime(
    *, model: str, total_ram: int, available_ram: int, cpu_score: int,
    cores: int, is_64_bit: bool, temperature: float = 0.0,
    storage_free: int = 0, battery_percent: int = 100,
    charging: bool = False, requested: str = "auto",
) -> Dict:
    total = max(0, int(total_ram))
    free = max(0, int(available_ram))
    cpu = max(0, min(100, int(cpu_score)))
    cores = max(1, int(cores))
    temp = float(temperature or 0.0)
    coarse = _coarse(total, free, cpu, is_64_bit, temp) if requested == "auto" else requested
    context, batch, ubatch, out_tokens, threads, timeout = _base_profile(coarse, cores)

    # Model-specific sustainable ceilings. The thermal governor can still lower
    # these values or use the cool-device burst headroom.
    if model == "max":
        if coarse == "flagship":
            context, out_tokens = min(context, 1536), min(out_tokens, 320)
        elif coarse == "performance":
            context, out_tokens = min(context, 1280), min(out_tokens, 224)
        else:
            context, out_tokens = min(context, 384), min(out_tokens, 64)
        batch, ubatch = min(batch, 24), min(ubatch, 12)
    elif model == "pro":
        if coarse == "flagship":
            context, out_tokens = min(context, 2560), min(out_tokens, 448)
        elif coarse == "performance":
            context, out_tokens = min(context, 1792), min(out_tokens, 304)
        elif coarse == "balanced":
            context, out_tokens = min(context, 896), min(out_tokens, 160)
        else:
            context, out_tokens = min(context, 384), min(out_tokens, 72)
        batch, ubatch = min(batch, 40), min(ubatch, 20)
    elif model == "ultra":
        if coarse in {"ultra_eco", "eco"}:
            context, out_tokens = min(context, 384), min(out_tokens, 64)
        elif coarse == "entry":
            context, out_tokens = min(context, 768), min(out_tokens, 128)
        elif coarse == "balanced":
            context, out_tokens = min(context, 1536), min(out_tokens, 256)
        elif coarse == "flagship":
            context, out_tokens = min(context, 3584), min(out_tokens, 640)
        else:
            context, out_tokens = min(context, 2560), min(out_tokens, 416)
        batch, ubatch = min(batch, 64), min(ubatch, 32)
    elif model == "smart":
        if coarse in {"ultra_eco", "eco"}:
            context, out_tokens = min(context, 512), min(out_tokens, 96)
        elif coarse == "entry":
            context, out_tokens = min(context, 896), min(out_tokens, 192)
        elif coarse == "balanced":
            context, out_tokens = min(context, 1792), min(out_tokens, 320)
        elif coarse == "flagship":
            context, out_tokens = min(context, 4096), min(out_tokens, 640)
        else:
            context, out_tokens = min(context, 3072), min(out_tokens, 480)
        batch, ubatch = min(batch, 80), min(ubatch, 40)
    elif model == "quality":
        context = min(2048 if coarse == "flagship" else 1792, context + (256 if free >= 900 * MiB else 0))
        out_tokens = min(384 if coarse == "flagship" else 352, out_tokens + (32 if free >= 900 * MiB else 0))
    else:
        context = min(context, 1536 if coarse == "flagship" else 1152)
        out_tokens = min(out_tokens, 288 if coarse == "flagship" else 240)

    # Avoid occupying every logical core. This normally gives better sustained
    # throughput because Android and Termux still need scheduling headroom.
    spare_core_limit = max(1, min(6, cores - 1 if cores > 1 else 1))
    if cpu < 20:
        threads = 1
    elif cpu < 40:
        threads = min(2, spare_core_limit)
    elif cpu < 60:
        threads = min(3, spare_core_limit)
    elif cpu < 78:
        threads = min(4, spare_core_limit)
    else:
        threads = spare_core_limit
    if cores <= 4:
        threads = min(threads, 2)

    guards = []
    if free < 230 * MiB:
        context, batch, ubatch, out_tokens, threads = 192, 8, 8, 40, 1
        coarse = "ultra_eco"
        guards.append("critical free RAM")
    elif free < 360 * MiB:
        context, batch, ubatch, out_tokens, threads = min(context, 320), min(batch, 12), 8, min(out_tokens, 64), 1
        guards.append("low free RAM")
    elif free < 520 * MiB:
        context, batch, ubatch, out_tokens = min(context, 448), min(batch, 24), min(ubatch, 12), min(out_tokens, 96)
        guards.append("limited free RAM")

    # Initial raw-temperature fallback. The sensor-aware governor applies the
    # real battery/skin/SoC thresholds immediately afterwards.
    if temp >= 88:
        threads, context, batch, ubatch, out_tokens = 1, 192, 8, 8, 32
        guards.append("emergency raw thermal sensor")
    elif temp >= 78:
        threads, context, batch, ubatch, out_tokens = 1, min(context, 384), 8, 8, min(out_tokens, 64)
        guards.append("critical raw thermal sensor")
    elif temp >= 68:
        threads, batch, out_tokens = min(2, threads), min(batch, 24), min(out_tokens, 144)
        guards.append("hot raw thermal sensor")

    if battery_percent and battery_percent <= 10 and not charging:
        threads, out_tokens, context = 1, min(out_tokens, 80), min(context, 448)
        guards.append("low battery")

    matching = [item for item in COMBINATION_TIERS if item["model"] == model]
    if not matching:
        matching = [item for item in COMBINATION_TIERS if item["model"] == "internal"]
    combo = matching[0]
    for item in matching:
        if total >= item["min_ram"] and free >= item["min_free"] and cpu >= item["min_cpu"]:
            combo = item

    qwen = model in {"smart", "ultra", "pro", "max"}
    return {
        "requested": requested,
        "model": model,
        "resolved": coarse,
        "combination_id": combo["id"],
        "threads": max(1, threads),
        "context": max(128, context),
        "batch": max(4, batch),
        "ubatch": max(4, min(batch, ubatch)),
        "max_tokens": max(32, out_tokens),
        "timeout": min(106, timeout),
        "temperature": 0.26 if qwen else (0.07 if model == "quality" else 0.08),
        "top_p": 0.90 if qwen else (0.84 if model == "quality" else 0.82),
        "repeat_penalty": 1.07 if qwen else 1.13,
        "memory_budget_bytes": max(80 * MiB, int(free * 0.70)),
        "guards": guards,
        "description": f"Burst-capable {combo['id']} plan: {threads} thread(s), context {context}, batch {batch}, {out_tokens} output tokens.",
    }


def recommend_configuration(scan: dict, compatibility: dict) -> Dict:
    total = int(scan.get("ram", {}).get("total", 0) or 0)
    free = int(scan.get("ram", {}).get("available", 0) or 0)
    processor = scan.get("processor", {})
    cpu = int(processor.get("score", 0) or 0)
    is64 = bool(processor.get("is_64_bit"))
    temp = float(scan.get("thermal", {}).get("maximum_celsius", 0) or 0)
    cores = int(processor.get("logical_cores", 1) or 1)
    battery = scan.get("battery", {})
    percent = int(battery.get("capacity_percent", 100) or 100)
    charging = str(battery.get("status", "")).casefold() in {"charging", "full"}

    model = "internal"
    reasons = []
    if free < 180 * MiB or not is64:
        reasons.append("live RAM or architecture requires the internal engine")
    elif compatibility.get("max", {}).get("compatible") and total >= 12000 * MiB and free >= 6300 * MiB and cpu >= 82:
        model = "max"; reasons.append("Qwen3 8B is the strongest sustainable installed match")
    elif compatibility.get("pro", {}).get("compatible") and total >= 7500 * MiB and free >= 3300 * MiB and cpu >= 66:
        model = "pro"; reasons.append("Qwen3 4B fits the live memory and CPU budget")
    elif compatibility.get("ultra", {}).get("compatible") and total >= 5000 * MiB and free >= 1600 * MiB and cpu >= 47:
        model = "ultra"; reasons.append("Qwen3 1.7B Q4_K_M is the strongest practical midrange match")
    elif compatibility.get("smart", {}).get("compatible") and total >= 3300 * MiB and free >= 950 * MiB and cpu >= 27:
        model = "smart"; reasons.append("Qwen3 0.6B Q8_0 fits the live budget")
    elif compatibility.get("quality", {}).get("compatible") and free >= 500 * MiB and cpu >= 22:
        model = "quality"; reasons.append("SmolLM2 Q4_1 is the strongest safe bundled fallback")
    elif compatibility.get("fast", {}).get("compatible"):
        model = "fast"; reasons.append("SmolLM2 Q2_K is the safe emergency model")
    else:
        reasons.append("transformer requirements are not currently satisfied")

    runtime_model = model if model != "internal" else "fast"
    plan = optimize_runtime(
        model=runtime_model, total_ram=total, available_ram=free, cpu_score=cpu,
        cores=cores, is_64_bit=is64, temperature=temp, battery_percent=percent,
        charging=charging,
    )

    if total < 900 * MiB or free < 150 * MiB or not is64:
        classifier = "micro"
    elif total < 1500 * MiB or free < 280 * MiB:
        classifier = "lite"
    elif total < 2400 * MiB or cpu < 22:
        classifier = "balanced"
    elif total < 3500 * MiB or cpu < 42:
        classifier = "standard"
    else:
        classifier = "max"

    if model == "internal":
        hybrid = "off"
    elif model in {"max", "pro", "ultra"} and free >= 2200 * MiB:
        hybrid = "fusion"
    elif model in {"smart", "quality"}:
        hybrid = "smart"
    else:
        hybrid = "speed"

    return {
        "gguf_model": model,
        "classifier_profile": classifier,
        "runtime_profile": plan["resolved"],
        "runtime_combination": plan["combination_id"],
        "runtime_plan": plan,
        "hybrid_mode": hybrid,
        "llm_mode": "always" if model != "internal" else "off",
        "selection_reasons": reasons,
    }
