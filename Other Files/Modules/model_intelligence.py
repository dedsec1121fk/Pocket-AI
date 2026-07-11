"""Per-model cognitive scaling for Pocket AI.

This module does not change GGUF weights. It makes every installed model use the
available evidence, context, output budget, and verification effort more
intelligently for its size and for the phone's live runtime envelope.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Mapping

MODULE_VERSION = 2

MODEL_COGNITIVE_PROFILES = {
    "fast": {
        "tier": "evidence extractor",
        "planning_steps": 2,
        "default_output": 176,
        "detailed_output": 232,
        "evidence_ratio": 0.72,
    },
    "quality": {
        "tier": "grounded compact reasoner",
        "planning_steps": 3,
        "default_output": 256,
        "detailed_output": 336,
        "evidence_ratio": 0.76,
    },
    "smart": {
        "tier": "small general reasoner",
        "planning_steps": 4,
        "default_output": 384,
        "detailed_output": 544,
        "evidence_ratio": 0.70,
    },
    "ultra": {
        "tier": "mid-size general reasoner",
        "planning_steps": 5,
        "default_output": 480,
        "detailed_output": 640,
        "evidence_ratio": 0.66,
    },
    "pro": {
        "tier": "advanced local reasoner",
        "planning_steps": 6,
        "default_output": 544,
        "detailed_output": 704,
        "evidence_ratio": 0.62,
    },
    "max": {
        "tier": "maximum local reasoner",
        "planning_steps": 7,
        "default_output": 608,
        "detailed_output": 768,
        "evidence_ratio": 0.60,
    },
}

_TASK_CHECKS_EN = {
    "math": "Recalculate every result, preserve units, and test the final value in the original problem.",
    "coding": "Check syntax, dependencies, paths, edge cases, and whether the command or code is directly runnable.",
    "comparison": "Use the same criteria for both sides, state the important trade-offs, and end with a clear conclusion.",
    "causal_explanation": "Separate correlation from causation and explain the mechanism in the correct order.",
    "recommendation": "Apply every user constraint before ranking options; explain the decisive trade-off.",
    "research": "Separate sourced facts, reasonable inferences, and uncertainty; do not invent citations.",
    "how_to": "Give ordered, executable steps and include the most likely failure point or safety check.",
    "factual_definition": "Give the definition first, then one useful example or distinction only when it adds value.",
    "school": "Match the learner's grade, define new vocabulary, show one worked example, and check understanding.",
}

_TASK_CHECKS_EL = {
    "math": "Ξαναϋπολόγισε κάθε αποτέλεσμα, κράτησε τις μονάδες και έλεγξε την τελική τιμή στο αρχικό πρόβλημα.",
    "coding": "Έλεγξε σύνταξη, εξαρτήσεις, διαδρομές, οριακές περιπτώσεις και αν ο κώδικας ή η εντολή εκτελείται άμεσα.",
    "comparison": "Χρησιμοποίησε τα ίδια κριτήρια και για τις δύο πλευρές, εξήγησε τα βασικά trade-offs και κλείσε με σαφές συμπέρασμα.",
    "causal_explanation": "Ξεχώρισε συσχέτιση από αιτιότητα και εξήγησε τον μηχανισμό με σωστή σειρά.",
    "recommendation": "Εφάρμοσε πρώτα όλους τους περιορισμούς του χρήστη και μετά κατάταξε τις επιλογές.",
    "research": "Ξεχώρισε τεκμηριωμένα γεγονότα, λογικά συμπεράσματα και αβεβαιότητα· μην επινοείς πηγές.",
    "how_to": "Δώσε εκτελέσιμα βήματα με σωστή σειρά και πρόσθεσε το πιθανότερο σημείο αποτυχίας ή ελέγχου ασφάλειας.",
    "factual_definition": "Δώσε πρώτα τον ορισμό και μετά μόνο ένα χρήσιμο παράδειγμα ή διάκριση.",
    "school": "Προσάρμοσε την εξήγηση στην τάξη, όρισε τη νέα ορολογία, δείξε ένα λυμένο παράδειγμα και έλεγξε την κατανόηση.",
}


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value).casefold())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", re.sub(r"[^0-9a-zα-ω]+", " ", value)).strip()


def _task_name(profile: Mapping | None) -> str:
    data = profile or {}
    if data.get("school_query"):
        return "school"
    return str(data.get("task") or "general_question")


def intelligence_instruction(model: str, language: str, task_profile: Mapping | None = None) -> str:
    """Return a compact instruction matched to the model's real capacity."""
    model = str(model or "quality").casefold()
    if model not in MODEL_COGNITIVE_PROFILES:
        model = "quality"
    profile = task_profile or {}
    task = _task_name(profile)
    detailed = str(profile.get("requested_depth", "standard")) == "detailed"
    greek = language == "el"
    check = (_TASK_CHECKS_EL if greek else _TASK_CHECKS_EN).get(task, "")

    if model == "fast":
        base = (
            "Δούλεψε ως ακριβής εξαγωγέας στοιχείων: (1) βρες τι ακριβώς ζητείται, "
            "(2) πάρε μόνο τα σχετικά τεκμήρια και το ασφαλές προσχέδιο, (3) δώσε σύντομη τελική απάντηση. "
            "Μην δημιουργείς νέο γεγονός, πηγή, ημερομηνία, εντολή ή υπολογισμό που δεν υποστηρίζεται."
            if greek else
            "Act as a precise evidence extractor: (1) identify exactly what is asked, "
            "(2) use only relevant evidence and the safe draft, (3) give a compact final answer. "
            "Do not create a new fact, source, date, command, or calculation that is not supported."
        )
    elif model == "quality":
        base = (
            "Κάνε ένα μικρό εσωτερικό πλάνο τριών βημάτων: πρόθεση, τεκμήρια, έλεγχος. "
            "Διόρθωσε το ασφαλές προσχέδιο μόνο όταν τα στοιχεία το δικαιολογούν. Απάντησε πρώτα άμεσα και μετά πρόσθεσε μόνο χρήσιμες λεπτομέρειες."
            if greek else
            "Use a small three-step internal plan: intent, evidence, verification. "
            "Correct the safe draft only when the evidence supports the change. Answer directly first, then add only useful detail."
        )
    elif model == "smart":
        base = (
            "Σχεδίασε σιωπηρά την απάντηση, εντόπισε όλους τους περιορισμούς, έλεγξε τις βασικές παραδοχές και σύνδεσε τα τεκμήρια σε φυσικό κείμενο. "
            "Ξεχώρισε γεγονότα από συμπεράσματα και κάνε έναν τελικό έλεγχο πληρότητας."
            if greek else
            "Privately plan the answer, capture every constraint, check key assumptions, and connect the evidence into natural prose. "
            "Separate facts from inferences and perform one final completeness check."
        )
    elif model == "ultra":
        base = (
            "Κάνε εσωτερική ανάλυση πρόθεσης, περιορισμών, εναλλακτικών και πιθανών λαθών. Επίλυσε αντιφάσεις στα στοιχεία, έλεγξε αριθμούς και κώδικα και γράψε μία συνεκτική τελική απάντηση."
            if greek else
            "Internally analyze intent, constraints, alternatives, and likely failure modes. Resolve evidence conflicts, verify numbers and code, and write one coherent final answer."
        )
    else:
        base = (
            "Εκτέλεσε πλήρη αλλά σύντομη εσωτερική διαδικασία: αποσύνθεση, έλεγχος τεκμηρίων, αντιπαραδείγματα, επανυπολογισμός, έλεγχος περιορισμών και τελική σύνθεση. "
            "Μην αποκαλύπτεις το εσωτερικό σχέδιο. Διατήρησε την απάντηση φυσική, ακριβή και πρακτική."
            if greek else
            "Run a complete but efficient internal process: decomposition, evidence check, counterexamples, recalculation, constraint audit, and final synthesis. "
            "Do not expose the internal plan. Keep the answer natural, precise, and practical."
        )
    if detailed:
        base += (
            " Δώσε αρκετή λεπτομέρεια για να μπορεί ο χρήστης να κατανοήσει και να εφαρμόσει την απάντηση."
            if greek else
            " Include enough detail for the user to understand and apply the answer."
        )
    if check:
        base += " " + check
    return base


def sampling_settings(model: str, task_profile: Mapping | None = None, runtime: Mapping | None = None) -> dict:
    """Return conservative sampling matched to model size and task type."""
    model = str(model or "quality").casefold()
    task = _task_name(task_profile)
    exact = task in {"math", "coding", "comparison", "causal_explanation", "research"}
    creative = task in {"creative_writing", "brainstorm", "story"}
    values = {
        "fast": {"temperature": 0.08, "top_p": 0.82, "top_k": 18, "min_p": 0.00, "presence_penalty": 0.00, "repeat_penalty": 1.14},
        "quality": {"temperature": 0.07, "top_p": 0.84, "top_k": 20, "min_p": 0.00, "presence_penalty": 0.00, "repeat_penalty": 1.13},
        "smart": {"temperature": 0.24, "top_p": 0.88, "top_k": 20, "min_p": 0.02, "presence_penalty": 0.15, "repeat_penalty": 1.08},
        "ultra": {"temperature": 0.28, "top_p": 0.90, "top_k": 24, "min_p": 0.02, "presence_penalty": 0.18, "repeat_penalty": 1.07},
        "pro": {"temperature": 0.30, "top_p": 0.91, "top_k": 28, "min_p": 0.02, "presence_penalty": 0.20, "repeat_penalty": 1.06},
        "max": {"temperature": 0.32, "top_p": 0.92, "top_k": 32, "min_p": 0.02, "presence_penalty": 0.20, "repeat_penalty": 1.06},
    }.get(model, {"temperature": 0.10, "top_p": 0.86, "top_k": 20, "min_p": 0.00, "presence_penalty": 0.00, "repeat_penalty": 1.12})
    values = dict(values)
    if exact:
        values["temperature"] = min(values["temperature"], 0.18 if model in {"smart", "ultra", "pro", "max"} else 0.06)
        values["top_p"] = min(values["top_p"], 0.86)
    elif creative:
        values["temperature"] = max(values["temperature"], 0.52 if model in {"smart", "ultra", "pro", "max"} else 0.20)
        values["top_p"] = max(values["top_p"], 0.92)
    if runtime and str(runtime.get("thermal_state", "")).casefold() in {"hot", "critical", "emergency"}:
        values["temperature"] = min(values["temperature"], 0.18)
    return values


def output_token_budget(model: str, runtime: Mapping, task_profile: Mapping | None = None, role: str = "answer") -> int:
    """Use all safe output headroom without exceeding the live runtime ceiling."""
    model = str(model or "quality").casefold()
    profile = MODEL_COGNITIVE_PROFILES.get(model, MODEL_COGNITIVE_PROFILES["quality"])
    task = _task_name(task_profile)
    detailed = str((task_profile or {}).get("requested_depth", "standard")) == "detailed"
    desired = int(profile["detailed_output"] if detailed else profile["default_output"])
    if task in {"coding", "school", "research", "how_to"}:
        desired = int(desired * 1.12)
    if role in {"analyst", "draft", "independent"}:
        desired = min(desired, 176 if model in {"fast", "quality"} else 256)
    elif role in {"final_critic", "verify"}:
        desired = min(desired, 224)
    ceiling = max(32, int(runtime.get("max_tokens", desired) or desired))
    return max(32, min(ceiling, desired))


def evidence_char_budget(model: str, runtime: Mapping, task_profile: Mapping | None = None) -> int:
    """Allocate prompt room to evidence while reserving answer and ChatML tokens."""
    model = str(model or "quality").casefold()
    context_tokens = max(128, int(runtime.get("context", 512) or 512))
    output_tokens = output_token_budget(model, runtime, task_profile)
    ratio = float(MODEL_COGNITIVE_PROFILES.get(model, MODEL_COGNITIVE_PROFILES["quality"])["evidence_ratio"])
    available_tokens = max(64, context_tokens - output_tokens - 150)
    return max(320, min(12000, int(available_tokens * 3.45 * ratio)))


def compress_evidence(query: str, evidence: str, max_chars: int, model: str = "quality") -> str:
    """Query-focus an evidence packet without asking a weak model to summarize it."""
    text = str(evidence or "").strip()
    if len(text) <= max_chars:
        return text
    query_terms = {token for token in _norm(query).split() if len(token) > 2}
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    ranked: list[tuple[float, int, str]] = []
    priority_markers = (
        "safe grounded draft", "reasoning blueprint", "exact", "verified", "school evidence",
        "trusted", "ασφαλες προσχεδιο", "σχεδιο συλλογισμου", "επαληθευ", "ακριβ",
    )
    for index, block in enumerate(blocks):
        normalized = _norm(block)
        terms = set(normalized.split())
        overlap = len(query_terms & terms)
        score = overlap * 2.5 + min(2.0, overlap / max(1, len(query_terms)) * 3.0)
        if any(marker in normalized for marker in priority_markers):
            score += 5.0
        if block.startswith(("[1]", "1.", "- ")):
            score += 0.4
        score -= index * 0.015
        ranked.append((score, index, block))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    chosen: list[tuple[int, str]] = []
    used = 0
    for _, index, block in ranked:
        remaining = max_chars - used
        if remaining < 80:
            break
        clipped = block[:remaining]
        chosen.append((index, clipped))
        used += len(clipped) + 2
    chosen.sort(key=lambda item: item[0])
    return "\n\n".join(block for _, block in chosen)[:max_chars]
