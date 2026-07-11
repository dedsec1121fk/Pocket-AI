"""Per-model cognitive scaling for Pocket AI.

This module does not change GGUF weights. It makes every installed model use the
available evidence, context, output budget, and verification effort more
intelligently for its size and for the phone's live runtime envelope.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Mapping

MODULE_VERSION = 4

MODEL_COGNITIVE_PROFILES = {
    "emergency_fast": {
        "tier": "135M emergency evidence extractor", "planning_steps": 2,
        "default_output": 144, "detailed_output": 192, "evidence_ratio": 0.78,
    },
    "emergency_quality": {
        "tier": "135M emergency grounded writer", "planning_steps": 3,
        "default_output": 192, "detailed_output": 256, "evidence_ratio": 0.80,
    },
    "fast": {
        "tier": "0.6B compact general reasoner", "planning_steps": 4,
        "default_output": 288, "detailed_output": 416, "evidence_ratio": 0.73,
    },
    "quality": {
        "tier": "0.8B compact bridge reasoner", "planning_steps": 4,
        "default_output": 336, "detailed_output": 480, "evidence_ratio": 0.71,
    },
    "smart": {
        "tier": "1.5B advanced compact reasoner", "planning_steps": 5,
        "default_output": 448, "detailed_output": 608, "evidence_ratio": 0.67,
    },
    "ultra": {
        "tier": "1.7B strongest compact reasoner", "planning_steps": 6,
        "default_output": 512, "detailed_output": 704, "evidence_ratio": 0.64,
    },
    "advanced": {
        "tier": "2B advanced extended reasoner", "planning_steps": 6,
        "default_output": 544, "detailed_output": 736, "evidence_ratio": 0.62,
    },
    "prime": {
        "tier": "3.09B maximum extended reasoner", "planning_steps": 7,
        "default_output": 608, "detailed_output": 832, "evidence_ratio": 0.60,
    },
    "pro": {
        "tier": "4B advanced local reasoner", "planning_steps": 7,
        "default_output": 640, "detailed_output": 896, "evidence_ratio": 0.59,
    },
    "max": {
        "tier": "8B maximum local reasoner", "planning_steps": 7,
        "default_output": 608, "detailed_output": 768, "evidence_ratio": 0.60,
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

    if model == "emergency_fast":
        base = (
            "Δούλεψε μόνο ως ακριβής εξαγωγέας τεκμηρίων: βρες το ζητούμενο, χρησιμοποίησε το ασφαλές προσχέδιο και δώσε σύντομη απάντηση χωρίς νέο μη τεκμηριωμένο γεγονός."
            if greek else
            "Act only as a precise evidence extractor: identify the request, use the safe grounded draft, and give a short answer without adding unsupported facts."
        )
    elif model == "emergency_quality":
        base = (
            "Χρησιμοποίησε μικρό πλάνο πρόθεση→τεκμήρια→έλεγχος. Διόρθωσε το ασφαλές προσχέδιο μόνο όταν τα στοιχεία το αποδεικνύουν."
            if greek else
            "Use a small intent→evidence→verification plan. Correct the safe draft only when the evidence proves the correction."
        )
    elif model == "fast":
        base = (
            "Σχεδίασε σιωπηρά τέσσερα βήματα: πρόθεση, περιορισμοί, σχετικά στοιχεία, τελικός έλεγχος. Απάντησε άμεσα και μη συμπληρώνεις κενά με εικασίες."
            if greek else
            "Privately use four steps: intent, constraints, relevant evidence, final check. Answer directly and never fill missing evidence with guesses."
        )
    elif model == "quality":
        base = (
            "Σύνδεσε τα στοιχεία σε φυσική απάντηση, έλεγξε αντιφάσεις και βασικές παραδοχές και κράτησε ξεχωριστά γεγονότα, συμπεράσματα και αβεβαιότητα."
            if greek else
            "Connect the evidence into a natural answer, check conflicts and key assumptions, and keep facts, inferences, and uncertainty distinct."
        )
    elif model == "smart":
        base = (
            "Αποσύνθεσε σιωπηρά το πρόβλημα, κάλυψε όλους τους περιορισμούς, σύγκρινε πιθανές λύσεις και επανέλεγξε αριθμούς, κώδικα και εντολές πριν γράψεις."
            if greek else
            "Privately decompose the problem, cover every constraint, compare plausible solutions, and recheck numbers, code, and commands before writing."
        )
    elif model == "ultra":
        base = (
            "Κάνε πλήρη αλλά αποδοτική ανάλυση πρόθεσης, περιορισμών, εναλλακτικών, αντιπαραδειγμάτων και πιθανών λαθών. Επίλυσε αντιφάσεις και γράψε μία συνεκτική τελική απάντηση."
            if greek else
            "Run a complete but efficient analysis of intent, constraints, alternatives, counterexamples, and likely failures. Resolve conflicts and write one coherent final answer."
        )
    elif model == "advanced":
        base = (
            "Χτίσε και έλεγξε δύο εναλλακτικές λύσεις, εντόπισε κρυφές παραδοχές, επανυπολόγισε κρίσιμα σημεία και σύνθεσε την πιο τεκμηριωμένη απάντηση."
            if greek else
            "Build and test two plausible solution paths, expose hidden assumptions, recalculate critical steps, and synthesize the best-supported answer."
        )
    elif model == "prime":
        base = (
            "Χρησιμοποίησε βαθιά αλλά χρονικά περιορισμένη αποσύνθεση, έλεγχο αντιπαραδειγμάτων, συνέπειας και τεκμηρίων και έπειτα γράψε την πιο ακριβή εφαρμόσιμη απάντηση."
            if greek else
            "Use deep but time-bounded decomposition, counterexample testing, consistency checks, and evidence auditing, then write the most accurate actionable answer."
        )
    else:
        base = (
            "Εκτέλεσε πλήρη εσωτερική διαδικασία αποσύνθεσης, ελέγχου τεκμηρίων, επανυπολογισμού, ελέγχου περιορισμών και τελικής σύνθεσης χωρίς να αποκαλύπτεις το εσωτερικό σχέδιο."
            if greek else
            "Run a complete internal process of decomposition, evidence checking, recalculation, constraint auditing, and final synthesis without exposing the private plan."
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
        "emergency_fast": {"temperature": 0.05, "top_p": 0.80, "top_k": 16, "min_p": 0.00, "presence_penalty": 0.00, "repeat_penalty": 1.15},
        "emergency_quality": {"temperature": 0.06, "top_p": 0.82, "top_k": 18, "min_p": 0.00, "presence_penalty": 0.00, "repeat_penalty": 1.14},
        "fast": {"temperature": 0.20, "top_p": 0.86, "top_k": 20, "min_p": 0.01, "presence_penalty": 0.10, "repeat_penalty": 1.10},
        "quality": {"temperature": 0.22, "top_p": 0.87, "top_k": 22, "min_p": 0.01, "presence_penalty": 0.12, "repeat_penalty": 1.09},
        "smart": {"temperature": 0.25, "top_p": 0.89, "top_k": 24, "min_p": 0.02, "presence_penalty": 0.15, "repeat_penalty": 1.08},
        "ultra": {"temperature": 0.28, "top_p": 0.90, "top_k": 26, "min_p": 0.02, "presence_penalty": 0.18, "repeat_penalty": 1.07},
        "advanced": {"temperature": 0.29, "top_p": 0.90, "top_k": 27, "min_p": 0.02, "presence_penalty": 0.19, "repeat_penalty": 1.07},
        "prime": {"temperature": 0.30, "top_p": 0.91, "top_k": 28, "min_p": 0.02, "presence_penalty": 0.20, "repeat_penalty": 1.06},
        "pro": {"temperature": 0.30, "top_p": 0.91, "top_k": 28, "min_p": 0.02, "presence_penalty": 0.20, "repeat_penalty": 1.06},
        "max": {"temperature": 0.32, "top_p": 0.92, "top_k": 32, "min_p": 0.02, "presence_penalty": 0.20, "repeat_penalty": 1.06},
    }.get(model, {"temperature": 0.18, "top_p": 0.86, "top_k": 20, "min_p": 0.00, "presence_penalty": 0.00, "repeat_penalty": 1.12})
    values = dict(values)
    if exact:
        values["temperature"] = min(values["temperature"], 0.18 if model not in {"emergency_fast", "emergency_quality"} else 0.06)
        values["top_p"] = min(values["top_p"], 0.86)
    elif creative:
        values["temperature"] = max(values["temperature"], 0.52 if model in {"quality", "smart", "ultra", "advanced", "prime", "pro", "max"} else 0.30)
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
        desired = min(desired, 176 if model in {"emergency_fast", "emergency_quality"} else 256)
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
