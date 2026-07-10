"""Route-aware answer confidence calibration for Pocket AI."""
from __future__ import annotations

from typing import Any, Dict

MODULE_VERSION = 1

_ROUTE_BASE = {
    "calculator": 0.99,
    "unit_conversion": 0.98,
    "retrieval_qa": 0.90,
    "retrieval_document": 0.80,
    "specialist_model": 0.76,
    "hybrid_cascade": 0.78,
    "hybrid_consensus": 0.80,
    "hybrid_adaptive": 0.77,
    "hybrid_expert": 0.79,
    "pattern": 0.72,
    "semantic": 0.64,
    "fallback": 0.25,
}


def calibrate(details: Dict[str, Any], response: str) -> Dict[str, Any]:
    route = str(details.get("route", ""))
    score = _ROUTE_BASE.get(route, 0.58)
    if route.startswith("hybrid_"):
        score = max(score, 0.72)
    numeric = details.get("confidence")
    if isinstance(numeric, (int, float)):
        score = 0.55 * score + 0.45 * max(0.0, min(1.0, float(numeric)))
    final_quality = details.get("final_quality")
    if isinstance(final_quality, dict) and isinstance(final_quality.get("score"), (int, float)):
        score = 0.55 * score + 0.45 * float(final_quality["score"])
    if len(response.strip()) < 12:
        score -= 0.08
    score = max(0.0, min(1.0, score))
    label = "high" if score >= 0.78 else "medium" if score >= 0.52 else "low"
    return {"score": round(score, 4), "label": label}
