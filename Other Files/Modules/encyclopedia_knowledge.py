"""Low-RAM offline encyclopedia retrieval for Pocket AI.

Searches sharded SQLite/FTS5 indexes derived from a plain-text Simple English
Wikipedia corpus. Only short relevant passages are returned, so a very small
LLM can answer with broad evidence without loading the corpus into memory.
"""
from __future__ import annotations

import json
import re
import sqlite3
import unicodedata
from pathlib import Path
from typing import Optional

MODULE_VERSION = 2
_STOP = {
    "a","an","the","of","to","for","in","on","at","by","with","from","and","or","as",
    "what","who","which","when","where","why","how","is","are","was","were","be","been",
    "do","does","did","can","could","would","should","tell","me","about","please","explain",
    "define","definition","meaning","information","facts","fact","give","describe","reason","reasons",
    "compare","comparison","versus","vs","difference","differences","between","work","works","working",
    "τι","ποιος","ποια","ποιο","ποτε","που","γιατι","πως","ειναι","ηταν","πες","μου",
    "για","εξηγησε","ο","η","το","οι","τα","του","της","των","σε","με","απο","και","ή",
    "συγκρινε","συγκριση","διαφορα","διαφορες","μεταξυ","λειτουργει","λογος","αιτια",
}

# Small cross-language bridge used only to form retrieval queries.  It does not
# translate answers; it lets Greek questions find the English encyclopedia.
_QUERY_ALIASES = {
    "tcp": ("Transmission Control Protocol",),
    "udp": ("User Datagram Protocol",),
    "http": ("Hypertext Transfer Protocol",),
    "https": ("HTTPS", "Hypertext Transfer Protocol Secure"),
    "ai": ("Artificial intelligence",),
    "ram": ("Random-access memory",),
    "cpu": ("Central processing unit",),
}

_EL_EN_BRIDGE = {
    "φωτοσυνθεση": ("photosynthesis",), "ηλιος": ("sun", "sunlight"),
    "ηλιακος": ("solar", "sunlight"), "ηλιακο": ("solar", "sunlight"),
    "φυτο": ("plant",), "φυτα": ("plants",), "ενεργεια": ("energy",),
    "νερο": ("water",), "οξυγονο": ("oxygen",), "διοξειδιο": ("dioxide", "carbon"),
    "ανθρακα": ("carbon",), "βαρυτητα": ("gravity",), "δυναμη": ("force",),
    "κινηση": ("motion",), "ηλεκτρισμος": ("electricity",), "ηλεκτρονιο": ("electron",),
    "ατομο": ("atom",), "μοριο": ("molecule",), "κυτταρο": ("cell",),
    "εγκεφαλος": ("brain",), "καρδια": ("heart",), "αιμα": ("blood",),
    "πιθανοτητα": ("probability",), "εξισωση": ("equation",), "κλασμα": ("fraction",),
    "γεωμετρια": ("geometry",), "αλγεβρα": ("algebra",), "ιστορια": ("history",),
    "γεωγραφια": ("geography",), "ελλαδα": ("greece",), "πρωτευουσα": ("capital",),
    "χωρα": ("country",), "πολεμος": ("war",), "υπολογιστης": ("computer",),
    "δικτυο": ("network",), "διαδικτυο": ("internet",), "ασφαλεια": ("security",),
    "κωδικας": ("code",), "προγραμματισμος": ("programming",), "συναρτηση": ("function",),
    "βαση": ("database",), "δεδομενα": ("data",), "τεχνητη": ("artificial",),
    "νοημοσυνη": ("intelligence", "ai"), "μοντελο": ("model",), "γλωσσα": ("language",),
    "μεταφραση": ("translation",), "θερμοκρασια": ("temperature",), "κλιμα": ("climate",),
    "πρωτοκολλο": ("protocol",), "συνδεση": ("connection",), "αξιοπιστια": ("reliability",),
}

_CURRENT_CUES = {
    "current","currently","today","latest","now","president","prime minister","ceo","price",
    "weather","score","standings","election","law","version","release","2025","2026","2027",
    "σημερα","τωρα","τελευταιο","προσφατο","προεδρος","πρωθυπουργος","τιμη","καιρος","εκλογες",
}


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value).casefold())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^0-9a-zα-ω]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _terms(value: str) -> list[str]:
    out: list[str] = []
    for token in _norm(value).split():
        if len(token) <= 1 or token in _STOP:
            continue
        if token not in out:
            out.append(token)
        for translated in _EL_EN_BRIDGE.get(token, ()):
            if translated not in out:
                out.append(translated)
    return out[:18]


def _subject(value: str) -> str:
    normalized = _norm(value)
    prefixes=(
        "what is ","what are ","who is ","who was ","tell me about ","explain ","define ",
        "information about ","facts about ","compare ","comparison of ","difference between ",
        "differences between ","why does ","why do ","how does ","how do ","how is ",
        "τι ειναι ","τι ηταν ","ποιος ειναι ","ποια ειναι ","πες μου για ","εξηγησε ",
        "πως λειτουργει ","γιατι ","συγκρινε ","συγκριση ","διαφορα μεταξυ ","διαφορες μεταξυ ",
    )
    for prefix in prefixes:
        if normalized.startswith(prefix):
            normalized=normalized[len(prefix):].strip()
            break
    return re.sub(r"^(?:a|an|the|ο|η|το|ενας|μια|ενα)\s+", "", normalized).strip()


def _query_variants(value: str) -> list[str]:
    """Create precise title/search variants for definitions and comparisons."""
    normalized = _norm(value)
    subject = _subject(value)
    variants: list[str] = []

    def add(candidate: str) -> None:
        candidate = re.sub(r"\s+", " ", candidate).strip(" ,;:?!.-")
        if candidate and candidate not in variants:
            variants.append(candidate)

    add(subject)
    for alias in _QUERY_ALIASES.get(subject, ()):
        add(alias)
    terms = _terms(subject or value)
    english_terms = [term for term in terms if re.fullmatch(r"[0-9a-z+#._/-]+", term)]
    if english_terms:
        add(" ".join(english_terms[:10]))

    comparison = any(cue in f" {normalized} " for cue in (
        " compare ", " comparison ", " versus ", " vs ", " difference ",
        " συγκρινε ", " συγκριση ", " διαφορα ", " διαφορες ",
    ))
    if comparison:
        # Search both sides independently. This prevents the task word
        # "compare" from outranking the entities themselves.
        split_text = subject
        for separator in (" versus ", " vs ", " and ", " και ", " με "):
            if separator in split_text:
                left, right = split_text.split(separator, 1)
                add(left)
                add(right)
                break
        for term in terms[:8]:
            add(term)
            for alias in _QUERY_ALIASES.get(term, ()):
                add(alias)
    elif len(terms) <= 5:
        for term in terms:
            add(term)

    # Keep the stripped subject first and never waste a query on generic task words.
    return variants[:10]


class EncyclopediaKnowledge:
    """Read-only sharded FTS retriever with tiny memory use."""

    def __init__(self, directory: Path) -> None:
        self.directory=Path(directory)
        self.manifest={}
        try:
            self.manifest=json.loads((self.directory/"manifest.json").read_text("utf-8"))
        except Exception:
            self.manifest={}
        listed=[self.directory/str(item.get("file", "")) for item in self.manifest.get("shards", [])]
        self.paths=[p for p in listed if p.is_file()] or sorted(self.directory.glob("PocketAI_SimpleWiki_*.sqlite3"))
        self.connections: dict[Path, sqlite3.Connection]={}
        self.article_count=int(self.manifest.get("articles",0) or 0)
        self.chunk_count=int(self.manifest.get("chunks",0) or 0)
        self.character_count=int(self.manifest.get("characters",0) or 0)

    @property
    def available(self) -> bool:
        return bool(self.paths)

    def _conn(self,path: Path) -> sqlite3.Connection:
        conn=self.connections.get(path)
        if conn is not None:
            return conn
        conn=sqlite3.connect(f"file:{path.as_posix()}?mode=ro&immutable=1",uri=True,check_same_thread=False,timeout=2.0)
        conn.row_factory=sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        conn.execute("PRAGMA cache_size=-1200")
        conn.execute("PRAGMA mmap_size=8388608")
        self.connections[path]=conn
        return conn

    @staticmethod
    def _make_item(row: sqlite3.Row, score: float, route: str) -> dict:
        return {
            "title":str(row["title"]).strip(),
            "text":str(row["text"]).strip(),
            "source_file":str(row["source_file"]),
            "article_no":int(row["article_no"]),
            "chunk_no":int(row["chunk_no"]),
            "score":float(score),
            "route":route,
        }

    def exact_title(self, subject: str, limit: int=4) -> list[dict]:
        target=_norm(subject)
        if not target:
            return []
        found=[]; seen=set()
        for path in self.paths:
            try:
                rows=self._conn(path).execute(
                    "SELECT * FROM chunks WHERE lower(title)=lower(?) ORDER BY chunk_no LIMIT ?",
                    (subject,max(2,limit)),
                ).fetchall()
                if not rows:
                    rows=self._conn(path).execute(
                        "SELECT * FROM chunks WHERE lower(title) LIKE lower(?) ORDER BY length(title),chunk_no LIMIT ?",
                        (target+"%",max(2,limit)),
                    ).fetchall()
            except sqlite3.Error:
                continue
            for row in rows:
                key=(str(row["title"]).casefold(),int(row["chunk_no"]))
                if key in seen: continue
                seen.add(key)
                similarity=1.0 if _norm(row["title"])==target else 0.87
                found.append(self._make_item(row,similarity,"encyclopedia_title"))
        found.sort(key=lambda x:(-x["score"],x["chunk_no"],len(x["title"])))
        return found[:limit]

    def search(self, query: str, limit: int=7) -> list[dict]:
        terms=_terms(query)
        if not terms:
            return []
        # AND first gives high precision; OR fallback improves recall.
        expressions=[" AND ".join('"'+t.replace('"','')+'"' for t in terms[:8])]
        if len(terms)>1:
            expressions.append(" OR ".join('"'+t.replace('"','')+'"' for t in terms[:10]))
        found=[]; seen=set(); query_set=set(terms)
        for expression_index,expression in enumerate(expressions):
            for path in self.paths:
                try:
                    rows=self._conn(path).execute(
                        "SELECT c.*, bm25(chunks_fts,5.5,1.0) AS rank "
                        "FROM chunks_fts JOIN chunks c ON c.id=chunks_fts.rowid "
                        "WHERE chunks_fts MATCH ? ORDER BY rank LIMIT ?",
                        (expression,max(3,limit)),
                    ).fetchall()
                except sqlite3.Error:
                    continue
                for row in rows:
                    key=(str(row["title"]).casefold(),int(row["chunk_no"]))
                    if key in seen: continue
                    title_terms=set(_terms(str(row["title"])))
                    text_terms=set(_terms(str(row["text"])[:1800]))
                    title_overlap=len(query_set & title_terms)/max(1,len(query_set))
                    body_overlap=len(query_set & text_terms)/max(1,len(query_set))
                    rank=abs(float(row["rank"] or 0.0))
                    rank_quality=1.0/(1.0+rank)
                    score=0.40+0.35*title_overlap+0.18*body_overlap+0.07*rank_quality-(0.05*expression_index)
                    seen.add(key)
                    found.append(self._make_item(row,min(0.96,max(0.30,score)),"encyclopedia_fts"))
            if len(found)>=limit:
                break
        found.sort(key=lambda x:(-x["score"],x["chunk_no"]))
        # Prefer diversity, but allow a second chunk from an exact/high-score article.
        selected=[]; per_title={}
        for item in found:
            key=item["title"].casefold()
            max_for_title=2 if item["score"]>=0.72 else 1
            if per_title.get(key,0)>=max_for_title:
                continue
            selected.append(item); per_title[key]=per_title.get(key,0)+1
            if len(selected)>=limit: break
        return selected

    def retrieve(self, query: str, limit: int=7) -> list[dict]:
        variants=_query_variants(query)
        if not variants:
            return []
        candidates=[]
        # Exact title retrieval for every entity is especially important for
        # A-vs-B questions and Greek-to-English bridge queries.
        for index, variant in enumerate(variants):
            for item in self.exact_title(variant,limit=min(3,limit)):
                adjusted=dict(item)
                adjusted["score"]=max(0.30,float(adjusted.get("score",0.0))-(0.025*index))
                adjusted["query_variant"]=variant
                candidates.append(adjusted)
        for index, variant in enumerate(variants):
            search_limit=max(3,min(limit,6))
            for item in self.search(variant,limit=search_limit):
                adjusted=dict(item)
                adjusted["score"]=max(0.30,float(adjusted.get("score",0.0))-(0.025*index))
                adjusted["query_variant"]=variant
                candidates.append(adjusted)

        seen=set(); result=[]; per_title={}
        for item in sorted(candidates,key=lambda x:(-x["score"],x.get("chunk_no",0))):
            key=(item["title"].casefold(),item["chunk_no"])
            if key in seen:
                continue
            title_key=item["title"].casefold()
            max_per_title=2 if float(item.get("score",0.0))>=0.76 else 1
            if per_title.get(title_key,0)>=max_per_title:
                continue
            seen.add(key)
            per_title[title_key]=per_title.get(title_key,0)+1
            result.append(item)
            if len(result)>=limit:
                break
        return result

    @staticmethod
    def _snippet(text: str, terms: list[str], max_chars: int) -> str:
        text=re.sub(r"\s+"," ",text).strip()
        if len(text)<=max_chars:
            return text
        lowered=_norm(text)
        positions=[lowered.find(term) for term in terms if lowered.find(term)>=0]
        pos=min(positions) if positions else 0
        start=max(0,pos-max_chars//4)
        end=min(len(text),start+max_chars)
        snippet=text[start:end].strip()
        if start>0: snippet="…"+snippet
        if end<len(text): snippet=snippet+"…"
        return snippet

    def answer(self, query: str, language: str="en") -> Optional[dict]:
        """Return a conservative direct extract only for exact, non-current English topics."""
        if language != "en" or not self.available:
            return None
        normalized=_norm(query)
        if any(cue in normalized.split() or cue in normalized for cue in _CURRENT_CUES):
            return None
        subject=_subject(query)
        if not subject or len(subject.split())>12:
            return None
        items=self.exact_title(subject,limit=3)
        exact=[item for item in items if _norm(item["title"])==_norm(subject)]
        if not exact:
            return None
        text=" ".join(item["text"] for item in exact[:2])
        sentences=re.split(r"(?<=[.!?])\s+",re.sub(r"\s+"," ",text).strip())
        chosen=[]; used=0
        for sentence in sentences:
            if len(sentence)<18:
                continue
            if used+len(sentence)>900 and chosen:
                break
            chosen.append(sentence); used+=len(sentence)+1
            if len(chosen)>=4 or used>=620:
                break
        if not chosen:
            return None
        response=" ".join(chosen).strip()
        return {
            "route":"encyclopedia_extract",
            "response":response,
            "title":exact[0]["title"],
            "score":exact[0]["score"],
            "source":"Offline Simple English Wikipedia snapshot",
            "static_snapshot":True,
        }

    def context(self, query: str, language: str="en", limit: int=6, max_chars: int=2800) -> str:
        if not self.available or max_chars<100:
            return ""
        items=self.retrieve(query,limit=limit)
        if not items:
            return ""
        terms=_terms(query)
        normalized=_norm(query)
        stale=any(cue in normalized.split() or cue in normalized for cue in _CURRENT_CUES)
        if language=="el":
            header="Offline εγκυκλοπαιδική πηγή (Simple English Wikipedia· μπορεί να είναι παλιά/ελλιπής"
            if stale: header += "· επαλήθευσε οπωσδήποτε το επίκαιρο στοιχείο"
            header += "):"
        else:
            header="Offline encyclopedia evidence (Simple English Wikipedia; may be incomplete or outdated"
            if stale: header += "; verify the time-sensitive claim"
            header += "):"
        lines=[header]; used=len(header)
        remaining=max_chars-used
        for item in items:
            allowance=max(120,min(620,remaining-len(item["title"])-8))
            if allowance<100: break
            snippet=self._snippet(item["text"],terms,allowance)
            line=f"- {item['title']}: {snippet}"
            if used+len(line)+1>max_chars:
                line=line[:max(0,max_chars-used-2)].rstrip()+"…"
            if len(line)<20: continue
            lines.append(line); used+=len(line)+1; remaining=max_chars-used
            if remaining<100: break
        return "\n".join(lines)

    def catalog(self, language: str="en") -> str:
        if language=="el":
            return (
                f"Offline εγκυκλοπαίδεια: {self.article_count:,} άρθρα / {self.chunk_count:,} αναζητήσιμα αποσπάσματα "
                f"σε {len(self.paths)} low-RAM shards. Το snapshot μπορεί να είναι ελλιπές ή παλιό."
            )
        return (
            f"Offline encyclopedia: {self.article_count:,} articles / {self.chunk_count:,} searchable passages "
            f"across {len(self.paths)} low-RAM shards. The snapshot may be incomplete or outdated."
        )

    def close(self) -> None:
        for conn in self.connections.values():
            try: conn.close()
            except Exception: pass
        self.connections.clear()
