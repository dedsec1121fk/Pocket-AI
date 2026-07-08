"""Persistent bilingual persona and natural-response helpers for Pocket AI."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict

MODULE_VERSION = 1

PERSONA_STYLES: Dict[str, Dict[str, str]] = {
    "friendly": {
        "label_en": "Friendly and natural",
        "label_el": "Φιλικό και φυσικό",
        "instruction_en": "Speak naturally, warmly, and clearly. Use ordinary conversational English without fake emotion or excessive filler.",
        "instruction_el": "Μίλα φυσικά, φιλικά και καθαρά. Χρησιμοποίησε καθημερινά Ελληνικά χωρίς ψεύτικο συναίσθημα ή περιττές φράσεις.",
    },
    "calm_expert": {
        "label_en": "Calm expert",
        "label_el": "Ήρεμος ειδικός",
        "instruction_en": "Sound like a calm, careful expert. Explain the important reasoning plainly and avoid jargon unless useful.",
        "instruction_el": "Μίλα σαν ήρεμος και προσεκτικός ειδικός. Εξήγησε καθαρά τη σημαντική λογική και απόφυγε την ορολογία όταν δεν χρειάζεται.",
    },
    "casual": {
        "label_en": "Casual companion",
        "label_el": "Χαλαρός συνομιλητής",
        "instruction_en": "Use relaxed, concise conversation while remaining accurate and respectful. Do not overuse slang.",
        "instruction_el": "Χρησιμοποίησε χαλαρή και σύντομη συζήτηση, παραμένοντας ακριβής και ευγενικός. Μην υπερβάλλεις με αργκό.",
    },
    "mentor": {
        "label_en": "Patient mentor",
        "label_el": "Υπομονετικός μέντορας",
        "instruction_en": "Teach patiently, break difficult ideas into practical steps, and encourage understanding without being patronizing.",
        "instruction_el": "Δίδαξε με υπομονή, χώρισε τις δύσκολες ιδέες σε πρακτικά βήματα και βοήθησε την κατανόηση χωρίς υποτιμητικό ύφος.",
    },
    "direct": {
        "label_en": "Direct assistant",
        "label_el": "Άμεσος βοηθός",
        "instruction_en": "Be direct, efficient, and factual. Give the answer first and only the detail needed to use it.",
        "instruction_el": "Να είσαι άμεσος, αποτελεσματικός και πραγματολογικός. Δώσε πρώτα την απάντηση και μόνο τις λεπτομέρειες που χρειάζονται.",
    },
}

DEFAULT_PERSONA: Dict[str, Any] = {
    "version": MODULE_VERSION,
    "assistant_name": "Pocket AI",
    "user_name": "",
    "style": "friendly",
    "human_style": True,
}

_NAME_RE = re.compile(r"[^0-9A-Za-zΑ-Ωα-ωΆ-ώΪΫϊϋΐΰ _'’\-]+", re.UNICODE)


def sanitize_name(value: str, fallback: str = "Pocket AI", maximum: int = 28) -> str:
    cleaned = _NAME_RE.sub("", str(value)).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)[:maximum].strip(" -_'’")
    return cleaned or fallback


def persona_path(data_dir: Path) -> Path:
    return Path(data_dir) / "persona.json"


def load_persona(data_dir: Path) -> Dict[str, Any]:
    result = dict(DEFAULT_PERSONA)
    path = persona_path(data_dir)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            result.update(payload)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        pass
    result["assistant_name"] = sanitize_name(result.get("assistant_name", "Pocket AI"))
    result["user_name"] = sanitize_name(result.get("user_name", ""), fallback="", maximum=36) if result.get("user_name") else ""
    if result.get("style") not in PERSONA_STYLES:
        result["style"] = "friendly"
    result["human_style"] = bool(result.get("human_style", True))
    result["version"] = MODULE_VERSION
    return result


def save_persona(data_dir: Path, payload: Dict[str, Any]) -> Dict[str, Any]:
    path = persona_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = dict(DEFAULT_PERSONA)
    clean.update(payload)
    clean["assistant_name"] = sanitize_name(clean.get("assistant_name", "Pocket AI"))
    clean["user_name"] = sanitize_name(clean.get("user_name", ""), fallback="", maximum=36) if clean.get("user_name") else ""
    if clean.get("style") not in PERSONA_STYLES:
        clean["style"] = "friendly"
    clean["human_style"] = bool(clean.get("human_style", True))
    clean["version"] = MODULE_VERSION
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(clean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return clean


def persona_instruction(config: Dict[str, Any], language: str) -> str:
    style = PERSONA_STYLES.get(str(config.get("style", "friendly")), PERSONA_STYLES["friendly"])
    name = sanitize_name(config.get("assistant_name", "Pocket AI"))
    user_name = str(config.get("user_name", "")).strip()
    if language == "el":
        instruction = (
            f"Το όνομά σου είναι {name}. Είσαι τοπικός βοηθός τεχνητής νοημοσύνης, όχι άνθρωπος. "
            + style["instruction_el"]
        )
        if user_name:
            instruction += f" Το όνομα του χρήστη είναι {user_name}, αλλά μη το επαναλαμβάνεις υπερβολικά."
    else:
        instruction = (
            f"Your name is {name}. You are a local AI assistant, not a human. "
            + style["instruction_en"]
        )
        if user_name:
            instruction += f" The user's name is {user_name}; use it sparingly, not in every reply."
    return instruction


def _outside_code_transform(text: str, transform) -> str:
    parts = re.split(r"(```.*?```)", text, flags=re.DOTALL)
    return "".join(part if part.startswith("```") else transform(part) for part in parts)


def naturalize_response(text: str, language: str, config: Dict[str, Any], route: str = "", seed_text: str = "") -> str:
    """Lightly naturalize prose while preserving code, commands, and factual content."""
    if not config.get("human_style", True):
        return text.strip()
    cleaned = text.strip()
    if not cleaned:
        return cleaned
    exact_routes = {"calculator", "unit_conversion", "time", "date", "system", "language_reject"}
    if route in exact_routes or cleaned.startswith(("```", "[", "{", "Model statistics")):
        return cleaned

    def english_transform(value: str) -> str:
        replacements = (
            (r"\bI am\b", "I'm"), (r"\bI do not\b", "I don't"),
            (r"\bI cannot\b", "I can't"), (r"\bIt is\b", "It's"),
            (r"\bThat is\b", "That's"), (r"\bYou can not\b", "You can't"),
        )
        for pattern, replacement in replacements:
            value = re.sub(pattern, replacement, value)
        return value

    if language == "en":
        cleaned = _outside_code_transform(cleaned, english_transform)
    cleaned = re.sub(r"(?i)\bas an ai language model,?\s*", "", cleaned).strip()

    style = str(config.get("style", "friendly"))
    digest = hashlib.sha256((seed_text + "\0" + cleaned).encode("utf-8", errors="ignore")).digest()
    add_lead = digest[0] % 5 == 0 and len(cleaned) > 55 and "\n" not in cleaned[:80]
    if add_lead and not re.match(r"^(sure|okay|certainly|of course|yes|no|βεβαιως|φυσικα|ενταξει|ναι|οχι)\b", cleaned, re.I):
        leads = {
            "friendly": (("Sure — ", "Absolutely — "), ("Βεβαίως — ", "Φυσικά — ")),
            "casual": (("Okay — ", "Got it — "), ("Εντάξει — ", "Το κατάλαβα — ")),
            "mentor": (("Let's work through it — ",), ("Ας το δούμε μαζί — ",)),
            "calm_expert": (("The practical answer is this: ",), ("Η πρακτική απάντηση είναι η εξής: ",)),
            "direct": ((), ()),
        }
        language_set = leads.get(style, leads["friendly"])[1 if language == "el" else 0]
        if language_set:
            cleaned = language_set[digest[1] % len(language_set)] + cleaned[0].lower() + cleaned[1:]

    user_name = str(config.get("user_name", "")).strip()
    if user_name and digest[2] % 11 == 0 and len(cleaned) < 900 and not cleaned.startswith(user_name):
        cleaned = f"{user_name}, " + cleaned[0].lower() + cleaned[1:]
    return cleaned.strip()


def describe_persona(config: Dict[str, Any], language: str = "en") -> str:
    style = PERSONA_STYLES.get(str(config.get("style", "friendly")), PERSONA_STYLES["friendly"])
    if language == "el":
        return (
            f"Όνομα AI: {config.get('assistant_name')}\n"
            f"Στυλ: {style['label_el']}\n"
            f"Ανθρώπινος τρόπος ομιλίας: {'ενεργός' if config.get('human_style') else 'ανενεργός'}\n"
            f"Όνομα χρήστη: {config.get('user_name') or 'δεν έχει οριστεί'}"
        )
    return (
        f"AI name: {config.get('assistant_name')}\n"
        f"Style: {style['label_en']}\n"
        f"Human-like conversation: {'enabled' if config.get('human_style') else 'disabled'}\n"
        f"User name: {config.get('user_name') or 'not set'}"
    )
