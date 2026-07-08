"""Sequential-response comparison for Pocket AI hybrid consensus mode."""
from __future__ import annotations

import re
from typing import Any, Dict, Tuple

MODULE_VERSION = 1
_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)


def _tokens(text: str) -> list[str]:
    return [token.casefold() for token in _TOKEN_RE.findall(text)]


def _base_score(question: str, answer: str) -> float:
    words = _tokens(answer)
    if not words:
        return 0.0
    score = 0.42
    unique_ratio = len(set(words)) / max(1, len(words))
    score += min(0.18, len(words) / 180.0)
    score += min(0.14, unique_ratio * 0.18)
    query = set(_tokens(question))
    if query:
        score += min(0.20, len(query & set(words)) / max(1, min(10, len(query))) * 0.24)
    if len(answer) > 3200:
        score -= 0.08
    if unique_ratio < 0.30:
        score -= 0.20
    return max(0.0, min(1.0, score))


def choose_consensus(question: str, first: str, second: str, first_quality: Dict[str, Any], second_quality: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    first_tokens = set(_tokens(first))
    second_tokens = set(_tokens(second))
    union = first_tokens | second_tokens
    agreement = len(first_tokens & second_tokens) / max(1, len(union))
    first_score = 0.58 * float(first_quality.get("score", 0.0)) + 0.42 * _base_score(question, first)
    second_score = 0.58 * float(second_quality.get("score", 0.0)) + 0.42 * _base_score(question, second)
    # Q4_1 is usually the stronger candidate; apply only a small tie-breaker.
    second_score += 0.025
    selected = second if second_score >= first_score else first
    return selected, {
        "agreement": round(agreement, 4),
        "fast_score": round(first_score, 4),
        "quality_score": round(second_score, 4),
        "selected": "quality" if selected is second else "fast",
    }
