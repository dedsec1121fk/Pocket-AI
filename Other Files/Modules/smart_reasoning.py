"""Deterministic planning, evidence compression and answer validation for Pocket AI.

The module is intentionally standard-library only.  It does not pretend to turn a
small language model into a frontier model; instead it protects the model from
irrelevant context and gives it a compact task-specific evidence packet.
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from typing import Iterable, Sequence

MODULE_VERSION = 3

_TOKEN_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)?", re.UNICODE)
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")

_STOP_EN = {
    "a", "an", "the", "and", "or", "but", "of", "to", "for", "in", "on", "at",
    "by", "with", "from", "as", "is", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "can", "could", "would", "should", "will", "may", "might",
    "what", "who", "which", "when", "where", "why", "how", "tell", "me", "please",
    "about", "explain", "describe", "give", "show", "this", "that", "these", "those",
}
_STOP_EL = {
    "ο", "η", "το", "οι", "τα", "του", "της", "των", "σε", "με", "για", "απο",
    "και", "ή", "η", "αλλα", "είναι", "ειναι", "ήταν", "ηταν", "να", "θα", "που",
    "τι", "ποιος", "ποια", "ποιο", "πότε", "ποτε", "πού", "γιατί", "γιατι", "πώς",
    "πως", "πες", "μου", "εξήγησε", "εξηγησε", "δώσε", "δωσε", "δείξε", "δειξε",
}

# Compact cross-language bridge for frequent Greek school, science, computing,
# and everyday concepts. It improves ranking of English encyclopedia passages
# without translating or expanding the entire prompt.
_EL_EN_BRIDGE = {
    "φωτοσυνθεση": ("photosynthesis",), "ηλιακο": ("solar", "sunlight"),
    "ηλιακος": ("solar", "sunlight"), "ηλιος": ("sun", "sunlight"),
    "ενεργεια": ("energy",), "φυτο": ("plant",), "φυτα": ("plants",),
    "νερο": ("water",), "οξυγονο": ("oxygen",), "διοξειδιο": ("dioxide", "carbon"),
    "βαρυτητα": ("gravity",), "δυναμη": ("force",), "κινηση": ("motion",),
    "ηλεκτρισμος": ("electricity",), "ηλεκτρονιο": ("electron",),
    "ατομο": ("atom",), "μοριο": ("molecule",), "κυτταρο": ("cell",),
    "νευρικο": ("nervous",), "συστημα": ("system",), "εγκεφαλος": ("brain",),
    "καρδια": ("heart",), "αιμα": ("blood",), "πιθανοτητα": ("probability",),
    "εξισωση": ("equation",), "κλασμα": ("fraction",), "ποσοστο": ("percentage",),
    "γεωμετρια": ("geometry",), "αλγεβρα": ("algebra",), "ιστορια": ("history",),
    "γεωγραφια": ("geography",), "ελλαδα": ("greece",), "ελληνικη": ("greek",),
    "πρωτευουσα": ("capital",), "χωρα": ("country",), "πολεμος": ("war",),
    "υπολογιστης": ("computer",), "δικτυο": ("network",), "διαδικτυο": ("internet",),
    "ασφαλεια": ("security",), "κωδικας": ("code",), "προγραμματισμος": ("programming",),
    "συναρτηση": ("function",), "βαση": ("database",), "δεδομενα": ("data",),
    "τεχνητη": ("artificial",), "νοημοσυνη": ("intelligence", "ai"),
    "μοντελο": ("model",), "γλωσσα": ("language",), "μεταφραση": ("translation",),
}

_TASK_CUES = {
    "comparison": (
        "compare", "comparison", "difference", "differences", "versus", " vs ", "better than",
        "pros and cons", "tradeoff", "διαφορα", "διαφορές", "σύγκρινε", "συγκρινε", "εναντιον",
        "καλύτερο από", "καλυτερο απο", "πλεονεκτήματα", "μειονεκτήματα",
    ),
    "how_to": (
        "how to", "steps", "guide", "tutorial", "install", "configure", "setup", "fix",
        "troubleshoot", "command", "procedure", "πως να", "βήματα", "βηματα", "οδηγός",
        "οδηγος", "εγκατάσταση", "εγκατασταση", "ρύθμιση", "ρυθμιση", "διόρθωσε", "διορθωσε",
    ),
    "causal_explanation": (
        "why", "how does", "how do", "reason", "cause", "effect", "mechanism", "explain why",
        "γιατί", "γιατι", "πώς λειτουργεί", "πως λειτουργει", "αιτία", "αιτια", "εξήγησε γιατί",
    ),
    "coding": (
        "code", "script", "python", "bash", "javascript", "java", "c++", "sql", "html", "css",
        "function", "class", "api", "error", "traceback", "termux", "github", "κώδικ", "σκριπτ",
        "συνάρτηση", "συναρτηση", "σφάλμα", "σφαλμα", "τερματικό", "τερματικο",
    ),
    "math": (
        "calculate", "solve", "equation", "proof", "prove", "derivative", "integral", "fraction",
        "geometry", "algebra", "probability", "υπολόγισε", "υπολογισε", "λύσε", "λυσε", "εξίσωση",
        "εξισωση", "απόδειξη", "αποδειξη", "παράγωγ", "ολοκλήρωμα", "κλάσμα",
    ),
    "summary": (
        "summarize", "summary", "shorten", "key points", "tl;dr", "σύνοψη", "συνοψη",
        "περίληψη", "περιληψη", "βασικά σημεία", "βασικα σημεια",
    ),
    "translation": (
        "translate", "translation", "in greek", "in english", "μετάφρασε", "μεταφρασε",
        "μετάφραση", "μεταφραση", "στα ελληνικά", "στα αγγλικά",
    ),
    "recommendation": (
        "recommend", "recommendation", "which should", "best for", "choose", "decision", "worth it",
        "πρότεινε", "προτεινε", "ποιο να", "καλύτερο για", "καλυτερο για", "επιλογή", "αξίζει",
    ),
    "creative": (
        "write a story", "poem", "brainstorm", "ideas", "creative", "roleplay", "γράψε ιστορία",
        "ποιημα", "ιδέες", "ιδεες", "δημιουργικό", "δημιουργικο",
    ),
}

_FACT_PREFIXES = (
    "what is ", "what are ", "who is ", "who was ", "when was ", "where is ", "where was ",
    "which country ", "capital of ", "define ", "meaning of ", "τι είναι ", "τι ειναι ",
    "ποιος είναι ", "ποια είναι ", "πότε ", "που είναι ", "ορισμός ", "σημασία ",
)

_CURRENT_CUES = {
    "current", "currently", "today", "latest", "now", "news", "weather", "price", "version",
    "president", "prime minister", "ceo", "score", "standings", "release", "law", "2025", "2026", "2027",
    "σημερα", "τωρα", "τελευταίο", "πρόσφατο", "καιρος", "τιμη", "έκδοση", "προεδρος", "πρωθυπουργος",
}


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFKD", str(text).casefold())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^0-9a-zα-ω+#._/-]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def tokens(text: str, language: str = "en", keep_stop: bool = False) -> list[str]:
    stop = _STOP_EL if language == "el" else _STOP_EN
    result: list[str] = []
    for token in _TOKEN_RE.findall(normalize(text)):
        if len(token) < 2:
            continue
        if not keep_stop and token in stop:
            continue
        result.append(token)
        if language == "el":
            for translated in _EL_EN_BRIDGE.get(token, ()):
                if translated not in result:
                    result.append(translated)
    return result


def _contains_any(normalized: str, cues: Iterable[str]) -> bool:
    padded = f" {normalized} "
    for cue in cues:
        cue_normalized = normalize(cue)
        if cue_normalized and (cue_normalized in normalized or f" {cue_normalized} " in padded):
            return True
    return False


def analyze_query(text: str, language: str = "en") -> dict:
    normalized = normalize(text)
    word_list = tokens(text, language, keep_stop=True)
    content = tokens(text, language)
    task = "general_question"
    for candidate, cues in _TASK_CUES.items():
        if _contains_any(normalized, cues):
            task = candidate
            break
    if task == "general_question":
        if any(normalized.startswith(normalize(prefix)) for prefix in _FACT_PREFIXES):
            task = "factual_definition"
        elif "?" not in text and len(word_list) <= 4:
            task = "factual_definition"
        elif normalized.startswith(("explain ", "describe ", "tell me about ", "εξηγησε ", "περιγραψε ")):
            task = "explanation"

    complexity = 0.08
    complexity += min(0.28, len(word_list) / 80.0)
    complexity += min(0.18, max(0, len(content) - 6) * 0.018)
    complexity += 0.12 * min(2, text.count("?") + text.count(";"))
    if "\n" in text or "```" in text:
        complexity += 0.15
    if re.search(r"\b(and|also|then|while|because|but|και|επισης|μετα|ενω|επειδη|αλλα)\b", normalized):
        complexity += 0.10
    if task in {"comparison", "causal_explanation", "how_to", "coding", "math", "recommendation"}:
        complexity += 0.22
    if task in {"summary", "translation", "creative"}:
        complexity += 0.16
    complexity = max(0.0, min(1.0, complexity))

    current_sensitive = any(normalize(cue) in normalized.split() or normalize(cue) in normalized for cue in _CURRENT_CUES)
    direct_ok = task == "factual_definition" and len(content) <= 8 and not current_sensitive
    use_llm = not direct_ok or task in {
        "comparison", "causal_explanation", "how_to", "coding", "math", "summary",
        "translation", "recommendation", "creative", "explanation",
    }

    style = {
        "comparison": "Give a direct verdict or distinction, then a compact comparison with concrete differences.",
        "how_to": "Give safe, ordered, executable steps. Include prerequisites and verification when relevant.",
        "causal_explanation": "State the main reason first, then explain the mechanism in logical order.",
        "coding": "Give working code or commands first, then explain important assumptions and failure cases.",
        "math": "Show the essential steps, check the result, and state the final answer clearly.",
        "summary": "Preserve the central meaning and return only the most important points.",
        "translation": "Translate faithfully while preserving tone and technical meaning.",
        "recommendation": "State the recommendation, the decisive criteria, trade-offs, and when another option is better.",
        "creative": "Follow the requested style and constraints without adding unrelated commentary.",
        "factual_definition": "Answer in the first sentence, then add only the most useful supporting detail.",
        "explanation": "Give a plain-language overview followed by the core mechanism or steps.",
    }.get(task, "Answer directly, explain the key reasoning, and avoid irrelevant filler.")

    detail_cues=("in detail","detailed","deep explanation","comprehensive","everything about","step by step","αναλυτικα","λεπτομερως","σε βαθος","ολα για","βημα βημα")
    simple_cues=("simple","simply","easy words","briefly","απλα","με απλα λογια","συντομα")
    requested_depth="detailed" if any(normalize(x) in normalized for x in detail_cues) else ("simple" if any(normalize(x) in normalized for x in simple_cues) else "standard")
    grade_match=re.search(r"\b(?:grade|class|year|ταξη)\s*(1[0-2]|[1-9])\b",normalized)
    grade=int(grade_match.group(1)) if grade_match else None
    school_cues=("grade","class","school","homework","lesson","curriculum","student","teacher","ταξη","σχολειο","εργασια","μαθημα","υλη","μαθητης","δασκαλος")
    school_query=grade is not None or any(normalize(x) in normalized for x in school_cues)
    if requested_depth=="detailed":
        complexity=min(1.0,complexity+0.20)
        direct_ok=False; use_llm=True
        style += " Cover prerequisites, mechanism, worked examples, common mistakes, connections, and a mastery check while staying organized."
    if school_query:
        style += " Adapt vocabulary and abstraction to the learner's grade, teach for understanding, and include a concrete example."

    return {
        "task": task,
        "complexity": round(complexity, 3),
        "current_sensitive": current_sensitive,
        "direct_ok": direct_ok,
        "use_llm": use_llm,
        "style_instruction": style,
        "content_terms": content[:24],
        "word_count": len(word_list),
        "requested_depth": requested_depth,
        "grade": grade,
        "school_query": school_query,
    }


def query_variants(text: str, language: str = "en") -> list[str]:
    normalized = normalize(text)
    variants = [text.strip()]
    prefixes = (
        "what is ", "what are ", "who is ", "who was ", "tell me about ", "explain ", "describe ",
        "how does ", "how do ", "how to ", "define ", "τι ειναι ", "ποιος ειναι ", "πες μου για ",
        "εξηγησε ", "περιγραψε ", "πως λειτουργει ", "πως να ",
    )
    subject = normalized
    for prefix in prefixes:
        if subject.startswith(prefix):
            subject = subject[len(prefix):].strip()
            break
    if subject and subject not in variants:
        variants.append(subject)
    key_terms = tokens(text, language)
    if key_terms:
        keyword_query = " ".join(key_terms[:12])
        if keyword_query not in variants:
            variants.append(keyword_query)
    # Preserve quoted phrases because they are often exact entities or error text.
    for quoted in re.findall(r"[\"'“”‘’]([^\"'“”‘’]{2,120})[\"'“”‘’]", text):
        quoted = quoted.strip()
        if quoted and quoted not in variants:
            variants.append(quoted)
    return variants[:5]


def _split_sentences(text: str) -> list[str]:
    clean = re.sub(r"\s+", " ", str(text)).strip()
    if not clean:
        return []
    sentences = [item.strip(" -\t") for item in _SENTENCE_RE.split(clean) if item.strip()]
    if len(sentences) == 1 and len(clean) > 420:
        # Long source passages without punctuation are sliced at safe word boundaries.
        words = clean.split()
        sentences = [" ".join(words[i:i + 55]) for i in range(0, len(words), 55)]
    return sentences


def _answer_type_bonus(sentence: str, task: str) -> float:
    normalized = normalize(sentence)
    bonus = 0.0
    if task == "causal_explanation" and any(x in normalized for x in ("because", "therefore", "causes", "due to", "επειδη", "διοτι", "προκαλει")):
        bonus += 0.14
    elif task == "how_to" and (re.search(r"\b(step|first|then|next|finally|run|install|open|create)\b", normalized) or re.search(r"\b(βημα|πρωτα|μετα|τελος|τρεξε|εγκαταστησε)\b", normalized)):
        bonus += 0.14
    elif task == "comparison" and any(x in normalized for x in ("whereas", "while", "unlike", "difference", "however", "ενω", "σε αντιθεση", "διαφορα")):
        bonus += 0.14
    elif task == "factual_definition" and re.match(r"^[^.!?]{1,100}\b(is|are|was|were|refers to|means|ειναι|σημαινει)\b", normalized):
        bonus += 0.12
    elif task == "coding" and any(x in sentence for x in ("`", "--", "()", "=", "/", "pkg ", "git ", "python ")):
        bonus += 0.10
    elif task == "math" and re.search(r"\d|[=+\-*/^]", sentence):
        bonus += 0.10
    return bonus


def rank_evidence(query: str, sources: Sequence[dict], language: str = "en", task_profile: dict | None = None) -> list[dict]:
    profile = task_profile or analyze_query(query, language)
    query_terms = tokens(query, language)
    query_counter = Counter(query_terms)
    query_set = set(query_terms)
    exact_subjects = [normalize(item) for item in query_variants(query, language)[1:]]
    ranked: list[dict] = []
    sentence_seen: list[str] = []

    for source_index, source in enumerate(sources):
        text = str(source.get("text") or source.get("response") or "").strip()
        if not text:
            continue
        title = str(source.get("title") or source.get("source") or source.get("source_type") or "Evidence").strip()
        source_score = float(source.get("score", 0.5) or 0.5)
        source_type = str(source.get("source_type") or source.get("kind") or "local")
        title_norm = normalize(title)
        title_terms = set(tokens(title, language))
        title_overlap = len(query_set & title_terms) / max(1, len(query_set))
        exact_title = any(subject and (subject == title_norm or subject in title_norm) for subject in exact_subjects)

        for sentence_index, sentence in enumerate(_split_sentences(text)):
            if len(sentence) < 12:
                continue
            sentence_norm = normalize(sentence)
            if any(SequenceMatcher(None, sentence_norm, prior).ratio() > 0.93 for prior in sentence_seen[-80:]):
                continue
            sentence_seen.append(sentence_norm)
            sentence_terms = tokens(sentence, language)
            sentence_set = set(sentence_terms)
            overlap_terms = query_set & sentence_set
            overlap = len(overlap_terms) / max(1, len(query_set))
            weighted = sum(1.0 + math.log1p(query_counter[t]) for t in overlap_terms) / max(1.0, len(query_set))
            phrase_bonus = 0.0
            query_norm = normalize(query)
            if query_norm and (query_norm in sentence_norm or sentence_norm in query_norm):
                phrase_bonus = 0.20
            position_bonus = max(0.0, 0.08 - sentence_index * 0.012)
            length_penalty = 0.0
            if len(sentence) > 520:
                length_penalty = min(0.12, (len(sentence) - 520) / 3200)
            score = (
                0.32 * max(0.0, min(1.0, source_score))
                + 0.30 * overlap
                + 0.12 * min(1.0, weighted)
                + 0.10 * title_overlap
                + (0.12 if exact_title else 0.0)
                + phrase_bonus
                + position_bonus
                + _answer_type_bonus(sentence, str(profile.get("task", "general_question")))
                - length_penalty
                - source_index * 0.002
            )
            ranked.append({
                "sentence": sentence,
                "title": title,
                "source_type": source_type,
                "score": round(max(0.0, min(1.25, score)), 4),
                "source_score": source_score,
                "exact_title": exact_title,
                "semantic_match": bool(overlap_terms or title_overlap > 0 or exact_title or phrase_bonus > 0),
                "matched_terms": sorted(overlap_terms)[:12],
            })

    ranked.sort(key=lambda item: (item["score"], item["exact_title"], item["source_score"]), reverse=True)
    has_semantic_matches = any(item.get("semantic_match") for item in ranked)
    selected: list[dict] = []
    per_title: Counter[str] = Counter()
    for item in ranked:
        if has_semantic_matches and not item.get("semantic_match") and float(item.get("score", 0.0)) < 0.62:
            continue
        key = normalize(item["title"])
        limit = 3 if item["exact_title"] else 2
        if per_title[key] >= limit:
            continue
        selected.append(item)
        per_title[key] += 1
        if len(selected) >= 18:
            break
    return selected


def build_evidence_packet(
    query: str,
    sources: Sequence[dict],
    language: str = "en",
    task_profile: dict | None = None,
    max_chars: int = 4200,
) -> tuple[str, list[dict]]:
    profile = task_profile or analyze_query(query, language)
    ranked = rank_evidence(query, sources, language, profile)
    if not ranked:
        return "", []

    # In A-vs-B questions, force evidence for both entities near the front.
    # Tiny models otherwise over-focus on whichever side had the highest BM25 score.
    if str(profile.get("task")) == "comparison":
        important = [term for term in profile.get("content_terms", []) if len(str(term)) > 1][:8]
        coverage: list[dict] = []
        used_ids: set[int] = set()
        for term in important:
            term_norm = normalize(str(term))
            for item in ranked:
                item_id = id(item)
                haystack = normalize(" ".join((str(item.get("title", "")), str(item.get("sentence", "")))))
                if item_id not in used_ids and re.search(r"(?<![0-9a-zα-ω])" + re.escape(term_norm) + r"(?![0-9a-zα-ω])", haystack):
                    coverage.append(item)
                    used_ids.add(item_id)
                    break
        ranked = coverage + [item for item in ranked if id(item) not in used_ids]

    lines: list[str] = []
    used = 0
    accepted: list[dict] = []
    for index, item in enumerate(ranked, start=1):
        title = re.sub(r"\s+", " ", item["title"]).strip()[:110]
        sentence = re.sub(r"\s+", " ", item["sentence"]).strip()
        if len(sentence) > 620:
            sentence = sentence[:617].rsplit(" ", 1)[0] + "…"
        rendered = f"[E{index}] {title}: {sentence}"
        if used + len(rendered) + 1 > max_chars:
            remaining = max_chars - used
            if remaining >= 120:
                rendered = rendered[:remaining].rsplit(" ", 1)[0] + "…"
            else:
                break
        lines.append(rendered)
        accepted.append({**item, "evidence_id": f"E{index}"})
        used += len(rendered) + 1
        if used >= max_chars:
            break
    return "\n".join(lines), accepted


def should_synthesize(task_profile: dict, evidence: Sequence[dict], language: str = "en") -> bool:
    if not evidence:
        return True
    if bool(task_profile.get("current_sensitive")):
        return True
    if not bool(task_profile.get("direct_ok")):
        return True
    # Greek questions often use English encyclopedia evidence and need translation/synthesis.
    if language == "el" and any(item.get("source_type") == "encyclopedia" for item in evidence[:4]):
        return True
    best = float(evidence[0].get("score", 0.0) or 0.0)
    return best < 0.72


def extractive_fallback(
    query: str,
    ranked_evidence: Sequence[dict],
    language: str = "en",
    task_profile: dict | None = None,
    max_sentences: int = 5,
) -> str:
    profile = task_profile or analyze_query(query, language)
    if not ranked_evidence:
        return ""
    chosen = [str(item.get("sentence", "")).strip() for item in ranked_evidence if str(item.get("sentence", "")).strip()]
    if not chosen:
        return ""
    task = str(profile.get("task", "general_question"))
    if task == "comparison" and len(chosen) >= 2:
        heading = "Key comparison:" if language != "el" else "Βασική σύγκριση:"
        return heading + "\n" + "\n".join(f"- {sentence}" for sentence in chosen[:max_sentences])
    if task in {"how_to", "coding"}:
        heading = "Best available steps:" if language != "el" else "Καλύτερα διαθέσιμα βήματα:"
        return heading + "\n" + "\n".join(f"{i}. {sentence}" for i, sentence in enumerate(chosen[:max_sentences], 1))
    if language == "el":
        greek_chars = sum(1 for char in " ".join(chosen[:max_sentences]) if "α" <= char.casefold() <= "ω")
        latin_chars = sum(1 for char in " ".join(chosen[:max_sentences]) if "a" <= char.casefold() <= "z")
        if latin_chars > max(20, greek_chars * 3):
            return "Σχετικές πληροφορίες από την offline αγγλική εγκυκλοπαίδεια:\n" + "\n".join(
                f"- {sentence}" for sentence in chosen[:max_sentences]
            )
    return " ".join(chosen[:max_sentences])


def validate_answer(answer: str, question: str, language: str = "en") -> dict:
    clean = str(answer).strip()
    issues: list[str] = []
    score = 0.55
    if not clean:
        return {"score": 0.0, "issues": ["empty"]}
    lowered = normalize(clean)
    if any(marker in clean for marker in ("<|im_start|>", "<|im_end|>", "RETRIEVED OFFLINE EVIDENCE", "QUESTION:")):
        issues.append("prompt leakage")
        score -= 0.35
    words = tokens(clean, language, keep_stop=True)
    if len(words) < 5:
        issues.append("too short")
        score -= 0.22
    elif len(words) >= 18:
        score += 0.08
    lines = [line.strip() for line in clean.splitlines() if line.strip()]
    if len(lines) >= 3 and len(set(normalize(line) for line in lines)) / len(lines) < 0.72:
        issues.append("repetitive")
        score -= 0.25
    question_terms = set(tokens(question, language))
    answer_terms = set(tokens(clean, language))
    if question_terms:
        overlap = len(question_terms & answer_terms) / max(1, min(10, len(question_terms)))
        score += min(0.20, overlap * 0.28)
        if overlap < 0.08 and len(question_terms) >= 3:
            issues.append("weak relevance")
            score -= 0.16
    if clean[-1:] not in ".!?`)]}" and len(clean) > 40:
        issues.append("possibly truncated")
        score -= 0.08
    repeated_phrases = re.findall(r"\b(.{12,60}?)\b(?:\s+\1\b)", lowered)
    if repeated_phrases:
        issues.append("repeated phrase")
        score -= 0.18
    return {"score": round(max(0.0, min(1.0, score)), 3), "issues": issues}


def clean_answer(answer: str) -> str:
    text = str(answer)
    text = text.replace("<|im_start|>", "").replace("<|im_end|>", "")
    text = re.sub(r"^(?:assistant|answer|final answer)\s*:\s*", "", text.strip(), flags=re.I)
    output: list[str] = []
    seen: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if output and output[-1] != "":
                output.append("")
            continue
        normalized = normalize(stripped)
        if any(SequenceMatcher(None, normalized, old).ratio() > 0.95 for old in seen[-20:]):
            continue
        seen.append(normalized)
        output.append(stripped)
    cleaned = "\n".join(output).strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned
