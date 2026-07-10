"""Continuous Android CPU/RAM/storage/thermal runtime optimizer for Pocket AI."""
from __future__ import annotations
from typing import Dict

MODULE_VERSION = 4
MiB = 1024 ** 2
GiB = 1024 ** 3

# Conservative operational bands. Qwen3 0.6B Q8_0 is allowed on A12-class
# 4 GB phones only with short context, one pass, sufficient live RAM, and thermal guards.
COMBINATION_TIERS = [
    {"id": "internal_critical", "min_ram": 0, "min_free": 0, "min_cpu": 0, "model": "internal", "profile": "ultra_eco"},
    {"id": "legacy_1gb", "min_ram": 512 * MiB, "min_free": 90 * MiB, "min_cpu": 0, "model": "internal", "profile": "ultra_eco"},
    {"id": "fast_2gb_slow", "min_ram": 1450 * MiB, "min_free": 280 * MiB, "min_cpu": 14, "model": "fast", "profile": "eco"},
    {"id": "quality_2gb_capable", "min_ram": 2050 * MiB, "min_free": 560 * MiB, "min_cpu": 25, "model": "quality", "profile": "entry"},
    {"id": "smart_4gb_entry", "min_ram": 3400 * MiB, "min_free": 900 * MiB, "min_cpu": 24, "model": "smart", "profile": "entry"},
    {"id": "smart_4gb_mid", "min_ram": 3600 * MiB, "min_free": 1250 * MiB, "min_cpu": 45, "model": "smart", "profile": "balanced"},
    {"id": "ultra_8gb_mid", "min_ram": 7000 * MiB, "min_free": 2500 * MiB, "min_cpu": 58, "model": "ultra", "profile": "balanced"},
    {"id": "ultra_12gb_strong", "min_ram": 10500 * MiB, "min_free": 3800 * MiB, "min_cpu": 75, "model": "ultra", "profile": "performance"},
]


def _coarse(total: int, available: int, cpu: int, is64: bool, temp: float) -> str:
    if (not is64) or total < 1450 * MiB or available < 230 * MiB:
        return "ultra_eco"
    if total < 2200 * MiB or available < 420 * MiB or cpu < 18:
        return "eco"
    if total < 3500 * MiB or available < 900 * MiB or cpu < 36:
        return "entry"
    if total < 5400 * MiB or available < 1500 * MiB or cpu < 66:
        return "balanced"
    return "performance"


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
    memory_budget = max(80 * MiB, int(free * 0.44))

    if coarse == "ultra_eco":
        context, batch, ubatch, out_tokens, threads, timeout = 320, 8, 8, 64, 1, 106
    elif coarse == "eco":
        context, batch, ubatch, out_tokens, threads, timeout = 448, 16, 8, 88, 1, 106
    elif coarse == "entry":
        context, batch, ubatch, out_tokens, threads, timeout = 768, 32, 16, 144, 2, 104
    elif coarse == "balanced":
        context, batch, ubatch, out_tokens, threads, timeout = 1280, 48, 24, 240, min(3, cores), 102
    else:
        context, batch, ubatch, out_tokens, threads, timeout = 2048, 64, 32, 352, min(4, cores), 100

    # Per-model ceilings and practical token budgets.
    if model == "ultra":
        if coarse in {"ultra_eco", "eco"}:
            context, out_tokens = min(context, 384), min(out_tokens, 64)
        elif coarse == "entry":
            context, out_tokens = min(context, 640), min(out_tokens, 112)
        elif coarse == "balanced":
            context, out_tokens = min(context, 1024), min(out_tokens, 192)
        else:
            context, out_tokens = min(context, 2048), min(out_tokens, 320)
        batch = min(batch, 48)
        ubatch = min(ubatch, 24)
    elif model == "smart":
        if coarse in {"ultra_eco", "eco"}:
            context = min(context, 512)
            out_tokens = min(out_tokens, 96)
        elif coarse == "entry":
            context = min(context, 768)
            out_tokens = min(out_tokens, 160)
        elif coarse == "balanced":
            context = min(context, 1280)
            out_tokens = min(out_tokens, 256)
        else:
            context = min(context, 2048)
            out_tokens = min(out_tokens, 384)
        batch = min(batch, 64)
    elif model == "quality":
        context = min(1536, context + (128 if free >= 900 * MiB else 0))
        out_tokens = min(320, out_tokens + (24 if free >= 900 * MiB else 0))
    else:
        context = min(context, 1024)
        out_tokens = min(out_tokens, 224)

    # LITTLE-core phones often slow down with excessive threads.
    if cpu < 20:
        threads = 1
    elif cpu < 42:
        threads = min(2, cores)
    elif cpu < 68:
        threads = min(3, cores)
    else:
        threads = min(4, cores)
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
    elif model == "ultra" and free < 2500 * MiB:
        context, batch, ubatch, out_tokens = min(context, 640), min(batch, 24), min(ubatch, 12), min(out_tokens, 96)
        guards.append("ultra model running in low-memory mode")
    elif model == "smart" and free < 900 * MiB:
        context, batch, ubatch, out_tokens = min(context, 512), min(batch, 24), min(ubatch, 12), min(out_tokens, 104)
        guards.append("smart model running in low-memory mode")

    if temp >= 52:
        threads, context, batch, ubatch, out_tokens = 1, min(context, 256), min(batch, 8), min(ubatch, 8), min(out_tokens, 48)
        guards.append("critical temperature")
    elif temp >= 47:
        threads, context, batch, ubatch, out_tokens = 1, min(context, 384), min(batch, 16), min(ubatch, 8), min(out_tokens, 72)
        guards.append("high temperature")
    elif temp >= 42:
        threads, batch, out_tokens = min(2, threads), min(batch, 32), min(out_tokens, 128)
        guards.append("warm device")

    if battery_percent and battery_percent <= 12 and not charging:
        threads, out_tokens, context = 1, min(out_tokens, 80), min(context, 448)
        guards.append("low battery")

    matching = [item for item in COMBINATION_TIERS if item["model"] == model]
    if not matching:
        matching = [item for item in COMBINATION_TIERS if item["model"] == "internal"]
    combo = matching[0]
    for item in matching:
        if total >= item["min_ram"] and free >= item["min_free"] and cpu >= item["min_cpu"]:
            combo = item

    # Qwen3 explicitly performs worse with greedy decoding. These settings keep
    # its hybrid reasoning usable while the output-token and wall-clock guards
    # still enforce the phone's two-minute target.
    temperature_setting = 0.60 if model in {"smart", "ultra"} else (0.10 if model == "quality" else 0.14)
    top_p = 0.95 if model in {"smart", "ultra"} else (0.86 if model == "quality" else 0.84)
    repeat_penalty = 1.05 if model in {"smart", "ultra"} else 1.12
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
        "temperature": temperature_setting,
        "top_p": top_p,
        "repeat_penalty": repeat_penalty,
        "memory_budget_bytes": memory_budget,
        "guards": guards,
        "description": f"Dynamic {combo['id']} plan using {threads} thread(s), context {context}, batch {batch}, and {out_tokens} output tokens.",
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
    if temp >= 52 or free < 180 * MiB:
        reasons.append("live RAM or temperature requires the internal engine")
    elif compatibility.get("ultra", {}).get("compatible") and total >= 7000 * MiB and free >= 2500 * MiB and cpu >= 58 and temp < 45:
        model = "ultra"
        reasons.append("the Qwen3 1.7B ultra model is the strongest safe live match")
    elif compatibility.get("smart", {}).get("compatible") and total >= 3400 * MiB and free >= 900 * MiB and cpu >= 24 and temp < 47:
        model = "smart"
        reasons.append("the Qwen3 0.6B smart model fits the live resource budget")
    elif compatibility.get("quality", {}).get("compatible") and free >= 560 * MiB and cpu >= 25:
        model = "quality"
        reasons.append("the 135M Q4 model is the strongest safe fallback")
    elif compatibility.get("fast", {}).get("compatible"):
        model = "fast"
        reasons.append("the 135M Q2 model is the strongest safe live match")
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
    elif model == "ultra":
        hybrid = "quality"
    elif model == "smart":
        hybrid = "quality" if free >= 900 * MiB else "smart"
    elif total >= 5400 * MiB and free >= 1450 * MiB and cpu >= 65 and temp < 43:
        hybrid = "adaptive"
    elif total >= 2500 * MiB and temp < 48:
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
