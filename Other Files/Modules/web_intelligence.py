"""No-key web-search planning helpers for Pocket AI.

The module does not silently modify model weights.  It supplies current public
information to the retrieval layer and can persist selected page text in the
local SQLite knowledge store.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Iterable, List, Mapping

MODULE_VERSION = 1

_CURRENT_CUES_EN = {
    "latest", "current", "currently", "today", "tonight", "this week",
    "this month", "this year", "recent", "recently", "news", "price",
    "weather", "score", "schedule", "version", "release", "update",
    "updated", "now", "live", "who is", "what happened",
}
_CURRENT_CUES_EL = {
    "τελευται", "σημερα", "τωρα", "προσφατ", "ειδησε", "καιρο",
    "τιμη", "σκορ", "προγραμμα", "εκδοση", "ενημερω", "ζωνταν",
    "ποιος ειναι", "τι συνεβη",
}
_EXPLICIT_CUES_EN = {
    "search the web", "search online", "search the internet", "look it up",
    "browse the web", "check online", "find online", "web search",
    "internet search", "research online", "verify online",
}
_EXPLICIT_CUES_EL = {
    "ψαξε στο διαδικτυο", "ψαξε online", "αναζητησε στο διαδικτυο",
    "δες online", "ελεγξε online", "βρες στο διαδικτυο", "κανε αναζητηση",
    "ερευνα στο διαδικτυο", "επιβεβαιωσε online",
}


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value).casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", re.sub(r"[^0-9a-zα-ω]+", " ", value)).strip()


def explicit_web_request(text: str) -> bool:
    normalized = _norm(text)
    return any(_norm(cue) in normalized for cue in (_EXPLICIT_CUES_EN | _EXPLICIT_CUES_EL))


def current_information_request(text: str) -> bool:
    normalized = _norm(text)
    return any(_norm(cue) in normalized for cue in (_CURRENT_CUES_EN | _CURRENT_CUES_EL))


def clean_web_query(text: str) -> str:
    value = str(text).strip()
    patterns = sorted(_EXPLICIT_CUES_EN | _EXPLICIT_CUES_EL, key=len, reverse=True)
    for cue in patterns:
        value = re.sub(re.escape(cue), " ", value, flags=re.I)
    value = re.sub(r"(?i)^\s*(?:please|can you|could you|θα μπορουσες|μπορεις να)\s+", "", value)
    value = re.sub(r"\s+", " ", value).strip(" .,:;?!")
    return value[:500] or str(text).strip()[:500]


def should_search(text: str, task_profile: Mapping | None, mode: str = "auto") -> bool:
    selected = str(mode or "auto").casefold().strip()
    if selected == "off":
        return False
    if explicit_web_request(text):
        return True
    if selected == "on":
        return True
    profile = task_profile or {}
    return bool(profile.get("current_sensitive")) or current_information_request(text)


def format_sources(results: Iterable[Mapping], language: str = "en", limit: int = 6) -> str:
    rows: List[str] = []
    for index, item in enumerate(results, 1):
        if index > max(1, int(limit)):
            break
        title = re.sub(r"\s+", " ", str(item.get("title") or "Source")).strip()
        url = str(item.get("url") or "").strip()
        provider = str(item.get("provider") or "web").strip()
        if not url:
            continue
        rows.append(f"[{index}] {title} — {provider}\n    {url}")
    if not rows:
        return "Δεν υπάρχουν διαθέσιμες πηγές." if language == "el" else "No web sources are available."
    heading = "Πηγές ιστού:" if language == "el" else "Web sources:"
    return heading + "\n" + "\n".join(rows)
