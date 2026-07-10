"""Human-readable hardware recommendation summaries for Pocket AI."""
from __future__ import annotations

from typing import Any, Dict

MODULE_VERSION = 1


def concise_reason(scan: Dict[str, Any], recommendation: Dict[str, Any], language: str = "en") -> str:
    ram = int(scan.get("ram", {}).get("total", 0) or 0) / (1024 ** 3)
    available = int(scan.get("ram", {}).get("available", 0) or 0) / (1024 ** 2)
    cpu = int(scan.get("processor", {}).get("score", 0) or 0)
    model = recommendation.get("gguf_model", "internal")
    profile = recommendation.get("runtime_profile", "auto")
    hybrid = recommendation.get("hybrid_mode", "auto")
    if language == "el":
        return f"Επιλέχθηκε {model} με {profile}/{hybrid}: RAM {ram:.1f} GB, διαθέσιμη {available:.0f} MB και βαθμολογία CPU {cpu}/100."
    return f"Selected {model} with {profile}/{hybrid}: {ram:.1f} GB RAM, {available:.0f} MB available, CPU score {cpu}/100."
