"""Resource-aware prompt context selection for Pocket AI."""
from __future__ import annotations

import re
from collections import Counter
from typing import Iterable, Sequence, Tuple

MODULE_VERSION = 1
_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)


def _terms(text: str) -> set[str]:
    return {token.casefold() for token in _TOKEN_RE.findall(text) if len(token) > 2}


def optimize_context(
    query: str,
    candidates: Sequence[dict],
    memories: Sequence[Tuple[str, str]],
    history: Iterable[Tuple[str, str]],
    max_chars: int = 4200,
) -> str:
    query_terms = _terms(query)
    pieces: list[tuple[float, str]] = []
    for index, candidate in enumerate(candidates[:10]):
        response = str(candidate.get("response", "")).strip()
        if not response:
            continue
        source = str(candidate.get("source", "")).strip()
        overlap = len(query_terms & _terms(response))
        base_score = float(candidate.get("score", 0.0) or 0.0)
        score = 3.0 * base_score + 0.55 * overlap - index * 0.04
        rendered = (f"Source: {source}\n" if source else "") + response[:1200]
        pieces.append((score, rendered))

    if memories:
        relevant = []
        for key, value in memories:
            combined = f"{key} {value}"
            overlap = len(query_terms & _terms(combined))
            if overlap or key.casefold() in {"name", "user_name", "creator", "project"}:
                relevant.append((overlap, f"{key} = {value}"))
        if relevant:
            relevant.sort(reverse=True)
            pieces.append((2.2, "Saved user facts:\n" + "\n".join(item[1] for item in relevant[:10])))

    history_rows = list(history)[-14:]
    selected_history = []
    for recency, (role, message) in enumerate(reversed(history_rows)):
        overlap = len(query_terms & _terms(message))
        if recency < 4 or overlap:
            selected_history.append((recency, role, message[:500], overlap))
    if selected_history:
        selected_history.sort(key=lambda item: item[0], reverse=True)
        transcript = "\n".join(f"{role.title()}: {message}" for _, role, message, _ in selected_history[-8:])
        pieces.append((1.8, "Recent conversation:\n" + transcript))

    pieces.sort(key=lambda item: item[0], reverse=True)
    output: list[str] = []
    used = 0
    for _, piece in pieces:
        if used >= max_chars:
            break
        remaining = max_chars - used
        clipped = piece[:remaining]
        if clipped:
            output.append(clipped)
            used += len(clipped) + 2
    return "\n\n".join(output)[:max_chars]
