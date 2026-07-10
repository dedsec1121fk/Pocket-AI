"""Fast sharded WordNet/Greek-WordNet retrieval for Pocket AI.

The module uses only Python's standard library.  It keeps the 117k-concept
lexicon in multiple read-only SQLite/FTS5 shards, so even low-RAM phones can
retrieve a handful of precise definitions without loading the corpus into RAM.
"""
from __future__ import annotations

import json
import re
import sqlite3
import unicodedata
from pathlib import Path
from typing import Iterable, Optional

MODULE_VERSION = 2

_STOP_EN = {
    "a", "an", "the", "of", "to", "for", "in", "on", "at", "by", "with", "from",
    "and", "or", "between", "what", "who", "which", "why", "how", "is", "are", "was",
    "were", "do", "does", "did", "define", "explain", "tell", "me", "about", "please",
    "meaning", "means", "compare", "comparison", "versus", "vs", "difference", "differences",
    "describe", "reason", "reasons", "work", "works", "working",
}
_STOP_EL = {
    "ο", "η", "το", "οι", "τα", "της", "του", "των", "σε", "με", "για", "απο", "και", "ή",
    "τι", "ποιος", "ποια", "ποιο", "πως", "γιατι", "ειναι", "ηταν", "ορισε", "εξηγησε", "πες", "μου",
    "στο", "στη", "στην", "στον", "στους", "στις", "ενος", "μιας", "εναν", "μια",
    "συγκρινε", "συγκριση", "διαφορα", "διαφορες", "μεταξυ", "περιγραψε", "λειτουργει", "λογος", "αιτια",
}

_EL_EN_BRIDGE = {
    "φωτοσυνθεση": ("photosynthesis",), "ηλιος": ("sun", "sunlight"),
    "φυτο": ("plant",), "φυτα": ("plants",), "ενεργεια": ("energy",),
    "νερο": ("water",), "οξυγονο": ("oxygen",), "διοξειδιο": ("dioxide", "carbon"),
    "βαρυτητα": ("gravity",), "δυναμη": ("force",), "κινηση": ("motion",),
    "ηλεκτρισμος": ("electricity",), "ηλεκτρονιο": ("electron",), "ατομο": ("atom",),
    "μοριο": ("molecule",), "κυτταρο": ("cell",), "εγκεφαλος": ("brain",),
    "καρδια": ("heart",), "αιμα": ("blood",), "πιθανοτητα": ("probability",),
    "εξισωση": ("equation",), "κλασμα": ("fraction",), "γεωμετρια": ("geometry",),
    "αλγεβρα": ("algebra",), "ιστορια": ("history",), "γεωγραφια": ("geography",),
    "ελλαδα": ("greece",), "πρωτευουσα": ("capital",), "χωρα": ("country",),
    "υπολογιστης": ("computer",), "δικτυο": ("network",), "διαδικτυο": ("internet",),
    "ασφαλεια": ("security",), "κωδικας": ("code",), "προγραμματισμος": ("programming",),
    "συναρτηση": ("function",), "βαση": ("database",), "δεδομενα": ("data",),
    "τεχνητη": ("artificial",), "νοημοσυνη": ("intelligence", "ai"),
    "πρωτοκολλο": ("protocol",), "συνδεση": ("connection",), "αξιοπιστια": ("reliability",),
}
_POS_EN = {"n": "noun", "v": "verb", "a": "adjective", "s": "adjective", "r": "adverb"}
_POS_EL = {"n": "ουσιαστικό", "v": "ρήμα", "a": "επίθετο", "s": "επίθετο", "r": "επίρρημα"}
_REL_LABEL_EN = {"@": "broader kind", "@i": "broader kind", "~": "more specific kind", "~i": "more specific kind", "!": "antonym", "&": "similar term", "=": "attribute", "+": "related form", "*": "entails", ">": "causes"}
_REL_LABEL_EL = {"@": "ευρύτερη έννοια", "@i": "ευρύτερη έννοια", "~": "ειδικότερη έννοια", "~i": "ειδικότερη έννοια", "!": "αντίθετο", "&": "παρόμοιος όρος", "=": "ιδιότητα", "+": "σχετική μορφή", "*": "συνεπάγεται", ">": "προκαλεί"}


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value).casefold())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.replace("_", " ")
    value = re.sub(r"[^0-9a-zα-ω]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _tokens(value: str, language: str = "en") -> list[str]:
    stop = _STOP_EL if language == "el" else _STOP_EN
    result: list[str] = []
    for token in _norm(value).split():
        if len(token) <= 1 or token in stop:
            continue
        if token not in result:
            result.append(token)
        if language == "el":
            for translated in _EL_EN_BRIDGE.get(token, ()):
                if translated not in result:
                    result.append(translated)
    return result


def _subject(text: str) -> tuple[str, str]:
    normalized = _norm(text)
    for pattern in (r"^what does (.+?) mean$", r"^what do (.+?) mean$", r"^τι σημαινει (.+)$"):
        match = re.match(pattern, normalized)
        if match:
            return match.group(1).strip(), "definition"
    patterns = (
        ("synonym", ("synonym of ", "synonyms of ", "another word for ", "συνωνυμο του ", "συνωνυμο της ", "συνωνυμα του ", "συνωνυμα της ")),
        ("antonym", ("antonym of ", "antonyms of ", "opposite of ", "αντιθετο του ", "αντιθετο της ", "αντωνυμο του ", "αντωνυμο της ")),
        ("hypernym", ("what kind of thing is ", "what type of thing is ", "τι ειδος ειναι ", "σε ποια κατηγορια ανηκει ")),
        ("definition", ("what is ", "what are ", "whats ", "define ", "definition of ", "meaning of ", "explain ", "tell me about ", "who is ", "who was ", "compare ", "comparison of ", "difference between ", "differences between ", "why does ", "why do ", "how does ", "how do ", "τι ειναι ", "τι ηταν ", "ορισε ", "ορισμος του ", "ορισμος της ", "σημασια του ", "σημασια της ", "εξηγησε ", "πες μου για ", "πως λειτουργει ", "γιατι ", "συγκρινε ", "συγκριση ", "διαφορα μεταξυ ", "διαφορες μεταξυ ")),
    )
    for intent, prefixes in patterns:
        for prefix in prefixes:
            if normalized.startswith(prefix):
                subject = normalized[len(prefix):].strip()
                subject = re.sub(r"^(?:a|an|the|ενα|ενας|μια|το|η|ο)\s+", "", subject)
                return subject, intent
    return normalized, "lookup"


def _variants(value: str, language: str) -> list[str]:
    base = _norm(value)
    result = [base] if base else []
    base = re.sub(r"^(?:a|an|the|ενα|ενας|μια|το|η|ο|οι|τα)\s+", "", base)
    if base and base not in result:
        result.append(base)
    words = base.split()
    if not words:
        return result
    word = words[-1]
    stems: list[str] = []
    if language == "en":
        if len(word) > 4 and word.endswith("ies"):
            stems.append(word[:-3] + "y")
        if len(word) > 4 and word.endswith("es"):
            stems.extend((word[:-2], word[:-1]))
        if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
            stems.append(word[:-1])
        if len(word) > 5 and word.endswith("ing"):
            stems.extend((word[:-3], word[:-3] + "e"))
        if len(word) > 4 and word.endswith("ed"):
            stems.extend((word[:-2], word[:-1]))
    else:
        endings = ("ους", "ων", "εις", "ες", "ος", "ης", "ας", "ου", "η", "α", "ο", "ι")
        for ending in endings:
            if len(word) > len(ending) + 3 and word.endswith(ending):
                stems.append(word[:-len(ending)])
                break
    for stem in stems:
        candidate = " ".join(words[:-1] + [stem]).strip()
        if candidate and candidate not in result:
            result.append(candidate)
    return result


class LexicalKnowledge:
    """Read-only multi-shard lexical retriever."""

    def __init__(self, directory: Path) -> None:
        self.directory = Path(directory)
        self.manifest_path = self.directory / "manifest.json"
        self.manifest: dict = {}
        self.paths: list[Path] = []
        self.connections: dict[Path, sqlite3.Connection] = {}
        try:
            self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except Exception:
            self.manifest = {}
        listed = [self.directory / str(item.get("filename", "")) for item in self.manifest.get("shards", [])]
        self.paths = [path for path in listed if path.is_file()]
        if not self.paths:
            self.paths = sorted(self.directory.glob("PocketAI_WordNet_*.sqlite3"))
        self.entry_count = int(self.manifest.get("total_synsets", 0) or 0)
        self.greek_count = int(self.manifest.get("greek_linked_synsets", 0) or 0)

    @property
    def available(self) -> bool:
        return bool(self.paths)

    def _conn(self, path: Path) -> sqlite3.Connection:
        conn = self.connections.get(path)
        if conn is not None:
            return conn
        uri = f"file:{path.as_posix()}?mode=ro&immutable=1"
        conn = sqlite3.connect(uri, uri=True, check_same_thread=False, timeout=2.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        conn.execute("PRAGMA cache_size=-1400")
        conn.execute("PRAGMA mmap_size=8388608")
        self.connections[path] = conn
        return conn

    @staticmethod
    def _row(row: sqlite3.Row, score: float = 1.0, route: str = "wordnet") -> dict:
        try:
            relations = json.loads(str(row["relations"]))
        except Exception:
            relations = []
        return {
            "id": str(row["id"]),
            "pos": str(row["pos"]),
            "pos_label": str(row["pos_label"]),
            "english_lemmas": [x.strip() for x in str(row["english_lemmas"]).split(";") if x.strip()],
            "greek_lemmas": [x.strip() for x in str(row["greek_lemmas"]).split(";") if x.strip()],
            "definition": str(row["definition"]).strip(),
            "examples": [x.strip() for x in str(row["examples"]).split(";") if x.strip()],
            "relations": relations,
            "score": float(score),
            "route": route,
        }

    def _lookup_id(self, synset_id: str) -> Optional[dict]:
        for path in self.paths:
            row = self._conn(path).execute("SELECT * FROM synsets WHERE id=?", (synset_id,)).fetchone()
            if row is not None:
                return self._row(row)
        return None

    def exact(self, phrase: str, language: str = "en", limit: int = 6) -> list[dict]:
        found: list[dict] = []
        seen: set[str] = set()
        for variant_index, variant in enumerate(_variants(phrase, language)):
            for path in self.paths:
                rows = self._conn(path).execute(
                    "SELECT s.*, l.sense_rank FROM lemmas l JOIN synsets s ON s.id=l.synset_id "
                    "WHERE l.normalized=? AND l.language=? ORDER BY l.sense_rank LIMIT ?",
                    (variant, language, max(24, limit * 8)),
                ).fetchall()
                for row in rows:
                    sid = str(row["id"])
                    if sid in seen:
                        continue
                    seen.add(sid)
                    # WordNet data files are ordered by lexicographer file, not by
                    # everyday sense frequency. Prefer head adjectives over rare
                    # satellite senses and favor bilingual senses for Greek queries.
                    pos = str(row["pos"])
                    head_bonus = 0.18 if pos in {"a", "n", "v", "r"} else 0.0
                    greek_bonus = 0.06 if language == "el" and str(row["greek_lemmas"]).strip() else 0.0
                    variant_penalty = 0.07 * variant_index
                    score = max(0.58, min(0.98, 0.76 + head_bonus + greek_bonus - variant_penalty))
                    found.append(self._row(row, score, "wordnet_exact"))
        found.sort(key=lambda item: item["score"], reverse=True)
        return found[:limit]

    def search(self, text: str, language: str = "en", limit: int = 8) -> list[dict]:
        terms = _tokens(text, language)[:10]
        if not terms:
            return []
        query = " OR ".join('"' + term.replace('"', '') + '"' for term in terms)
        found: list[dict] = []
        seen: set[str] = set()
        query_set = set(terms)
        for path in self.paths:
            try:
                rows = self._conn(path).execute(
                    "SELECT s.*, bm25(wordnet_fts, 0.0, 5.5, 5.5, 2.2, 0.6) AS rank "
                    "FROM wordnet_fts JOIN synsets s ON s.id=wordnet_fts.synset_id "
                    "WHERE wordnet_fts MATCH ? ORDER BY rank LIMIT ?",
                    (query, max(3, limit)),
                ).fetchall()
            except sqlite3.Error:
                continue
            for row in rows:
                sid = str(row["id"])
                if sid in seen:
                    continue
                hay = " ".join((str(row["english_lemmas"]), str(row["greek_lemmas"]), str(row["definition"])))
                overlap = len(query_set & set(_tokens(hay, language))) / max(1, len(query_set))
                rank = abs(float(row["rank"] or 0.0))
                rank_quality = 1.0 / (1.0 + rank)
                score = min(0.94, 0.48 + 0.34 * overlap + 0.12 * rank_quality)
                seen.add(sid)
                found.append(self._row(row, score, "wordnet_fts"))
        found.sort(key=lambda item: item["score"], reverse=True)
        return found[:limit]

    def retrieve(self, text: str, language: str = "en", limit: int = 6) -> list[dict]:
        subject, _ = _subject(text)
        candidates = self.exact(subject, language, limit=max(3, limit))
        meaningful = _tokens(subject, language)
        # Exact lookup of individual entities is essential for comparisons.
        # For Greek queries, bridge tokens are also checked in English.
        if len(subject.split()) > 1 or len(meaningful) > 1:
            for token in meaningful[:8]:
                candidates.extend(self.exact(token, language, limit=2))
                if language == "el" and re.fullmatch(r"[0-9a-z][0-9a-z+#._/-]*", token):
                    candidates.extend(self.exact(token, "en", limit=2))
        candidates.extend(self.search(subject or text, language, limit=max(4, limit)))
        query_terms = set(_tokens(text, language))
        seen: set[str] = set()
        ranked: list[dict] = []
        for item in candidates:
            if item["id"] in seen:
                continue
            seen.add(item["id"])
            evidence = " ".join(item["english_lemmas"] + item["greek_lemmas"] + [item["definition"]])
            overlap = len(query_terms & set(_tokens(evidence, language))) / max(1, len(query_terms))
            item = dict(item)
            item["score"] = min(1.0, float(item["score"]) + 0.16 * overlap)
            ranked.append(item)
        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked[:limit]

    def _relation_items(self, item: dict, symbols: Iterable[str], limit: int = 6) -> list[dict]:
        wanted = set(symbols)
        results: list[dict] = []
        seen: set[str] = set()
        for symbol, target in item.get("relations", []):
            if symbol not in wanted or target in seen:
                continue
            related = self._lookup_id(str(target))
            if related:
                related["relation"] = symbol
                results.append(related)
                seen.add(str(target))
                if len(results) >= limit:
                    break
        return results

    def answer(self, text: str, language: str = "en") -> Optional[dict]:
        subject, intent = _subject(text)
        if not subject or len(subject.split()) > 8:
            return None
        senses = self.exact(subject, language, limit=4)
        if not senses:
            return None
        main = senses[0]
        lemma_list = main["greek_lemmas"] if language == "el" and main["greek_lemmas"] else main["english_lemmas"]
        display = lemma_list[0] if lemma_list else subject
        pos = _POS_EL.get(main["pos"], main["pos_label"]) if language == "el" else _POS_EN.get(main["pos"], main["pos_label"])

        if intent == "synonym":
            synonyms: list[str] = []
            for sense in senses[:3]:
                pool = sense["greek_lemmas"] if language == "el" and sense["greek_lemmas"] else sense["english_lemmas"]
                for value in pool:
                    if _norm(value) != _norm(subject) and value not in synonyms:
                        synonyms.append(value)
            # Adjective head synsets often encode useful near-synonyms through
            # "similar-to" pointers rather than in the same lemma list.
            if len(synonyms) < 3:
                for sense in senses[:3]:
                    for related in self._relation_items(sense, {"&"}, limit=8):
                        pool = related["greek_lemmas"] if language == "el" and related["greek_lemmas"] else related["english_lemmas"]
                        for value in pool:
                            if _norm(value) != _norm(subject) and value not in synonyms:
                                synonyms.append(value)
            if not synonyms:
                return None
            response = (f"Συνώνυμα ή κοντινές λέξεις του «{display}»: " if language == "el" else f"Synonyms or close words for “{display}”: ") + ", ".join(synonyms[:12]) + "."
            return {"response": response, "route": "wordnet_synonyms", "knowledge_id": main["id"], "match_score": main["score"]}

        if intent == "antonym":
            related: list[dict] = []
            seen_related: set[str] = set()
            # Antonym pointers can live on a different sense than the first one.
            for sense in senses:
                for related_item in self._relation_items(sense, {"!"}, limit=8):
                    if related_item["id"] not in seen_related:
                        seen_related.add(related_item["id"])
                        related.append(related_item)
            values: list[str] = []
            for item in related:
                pool = item["greek_lemmas"] if language == "el" and item["greek_lemmas"] else item["english_lemmas"]
                for value in pool:
                    if value not in values:
                        values.append(value)
            if not values:
                return None
            response = (f"Αντίθετα του «{display}»: " if language == "el" else f"Antonyms of “{display}”: ") + ", ".join(values[:10]) + "."
            return {"response": response, "route": "wordnet_antonyms", "knowledge_id": main["id"], "match_score": main["score"]}

        if intent == "hypernym":
            related = self._relation_items(main, {"@", "@i"}, limit=5)
            values: list[str] = []
            for item in related:
                pool = item["greek_lemmas"] if language == "el" and item["greek_lemmas"] else item["english_lemmas"]
                if pool:
                    values.append(pool[0])
            if values:
                response = (f"Το «{display}» ανήκει ευρύτερα στις έννοιες: " if language == "el" else f"“{display}” is a kind of: ") + ", ".join(values) + "."
                return {"response": response, "route": "wordnet_hypernym", "knowledge_id": main["id"], "match_score": main["score"]}

        # English definitions are safe to answer directly. Greek definitions are
        # injected as evidence for the local model, which can render them naturally.
        if language == "el":
            greek_terms = ", ".join(main["greek_lemmas"][:8]) or display
            english_terms = ", ".join(main["english_lemmas"][:8])
            response = f"«{display}» ({pos}). Αγγλικός ορισμός: {main['definition']}"
            if english_terms:
                response += f" Αγγλικοί όροι: {english_terms}."
            if greek_terms:
                response += f" Ελληνικοί όροι: {greek_terms}."
            return {"response": response, "route": "wordnet_definition_bilingual", "knowledge_id": main["id"], "match_score": main["score"], "requires_generation": True}

        lines = [f"“{display}” ({pos}): {main['definition']}"]
        synonyms = [x for x in main["english_lemmas"] if _norm(x) != _norm(display)]
        if synonyms:
            lines.append("Synonyms: " + ", ".join(synonyms[:8]) + ".")
        if main["examples"]:
            lines.append("Example: " + main["examples"][0] + ".")
        # Add a second sense only when it is genuinely distinct.
        if len(senses) > 1 and senses[1]["definition"] != main["definition"]:
            lines.append(f"Another common sense ({_POS_EN.get(senses[1]['pos'], senses[1]['pos_label'])}): {senses[1]['definition']}")
        return {"response": "\n".join(lines), "route": "wordnet_definition", "knowledge_id": main["id"], "match_score": main["score"]}

    def context(self, text: str, language: str = "en", limit: int = 7, max_chars: int = 3000) -> str:
        pieces: list[str] = []
        total = 0
        for item in self.retrieve(text, language, limit=limit):
            en = ", ".join(item["english_lemmas"][:6])
            el = ", ".join(item["greek_lemmas"][:6])
            label = el if language == "el" and el else en
            pos = _POS_EL.get(item["pos"], item["pos_label"]) if language == "el" else _POS_EN.get(item["pos"], item["pos_label"])
            if language == "el" and el:
                line = f"- {label} ({pos}); English equivalents: {en}. Definition: {item['definition']}"
            else:
                line = f"- {label} ({pos}): {item['definition']}"
            if item["examples"]:
                line += f" Example: {item['examples'][0]}"
            if total + len(line) > max_chars:
                break
            pieces.append(line)
            total += len(line) + 1
        return "\n".join(pieces)

    def catalog(self, language: str = "en") -> str:
        if language == "el":
            return f"Λεξιλογική βάση WordNet: {self.entry_count:,} έννοιες, με {self.greek_count:,} έννοιες συνδεδεμένες με ελληνικούς όρους, σε {len(self.paths)} γρήγορα SQLite shards."
        return f"WordNet lexical foundation: {self.entry_count:,} concepts, including {self.greek_count:,} concepts linked to Greek terms, across {len(self.paths)} fast SQLite shards."

    def close(self) -> None:
        for conn in self.connections.values():
            try:
                conn.close()
            except Exception:
                pass
        self.connections.clear()
