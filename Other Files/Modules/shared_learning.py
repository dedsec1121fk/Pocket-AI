"""Shared, retrieval-based learning for every Pocket AI model.

This module does not change GGUF weights.  It stores compact, verified lessons
from high-confidence local answers and trusted web evidence, then gives those
lessons to every installed model on later questions.  A stronger model can
therefore teach the small emergency models without unsafe on-device fine-tuning.
"""
from __future__ import annotations

import datetime as _dt
import difflib
import hashlib
import json
import re
import sqlite3
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence

MODULE_VERSION = 2
_TOKEN_RE = re.compile(r"[0-9a-zα-ω]+", re.I)


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def _norm(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value).casefold())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return " ".join(_TOKEN_RE.findall(text))


def _tokens(value: str) -> list[str]:
    return [token for token in _norm(value).split() if len(token) > 1][:80]


def _fingerprint(query: str, language: str) -> str:
    payload = language + "|" + _norm(query)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _compact(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", str(text)).strip()
    if len(text) <= limit:
        return text
    clipped = text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:")
    return clipped + "…"


class SharedLearningEngine:
    """Persistent lesson bridge shared by every local model tier."""

    STRENGTH = {
        "emergency_fast": 0.8,
        "emergency_quality": 1.0,
        "fast": 1.8,
        "quality": 2.2,
        "smart": 3.0,
        "ultra": 3.4,
        "pro": 4.2,
        "max": 5.0,
        "grounded": 2.8,
        "web": 2.7,
    }

    def __init__(self, data_dir: Path) -> None:
        self.path = Path(data_dir) / "shared_model_learning.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.path), timeout=20.0)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA synchronous=NORMAL")
        self.connection.execute("PRAGMA temp_store=MEMORY")
        self._create_schema()

    def _create_schema(self) -> None:
        with self.connection:
            self.connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS lessons (
                    fingerprint TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    normalized_query TEXT NOT NULL,
                    language TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    evidence TEXT NOT NULL DEFAULT '',
                    sources_json TEXT NOT NULL DEFAULT '[]',
                    teacher_model TEXT NOT NULL DEFAULT 'grounded',
                    confidence REAL NOT NULL DEFAULT 0.0,
                    strength REAL NOT NULL DEFAULT 1.0,
                    uses INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_lessons_language
                    ON lessons(language);
                CREATE INDEX IF NOT EXISTS idx_lessons_updated
                    ON lessons(updated_at);

                CREATE TABLE IF NOT EXISTS lesson_terms (
                    term TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    frequency REAL NOT NULL DEFAULT 1.0,
                    PRIMARY KEY(term, fingerprint),
                    FOREIGN KEY(fingerprint) REFERENCES lessons(fingerprint)
                        ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_lesson_terms_fingerprint
                    ON lesson_terms(fingerprint);
                """
            )

    def close(self) -> None:
        self.connection.close()

    @staticmethod
    def _safe_answer(answer: str) -> bool:
        normalized = _norm(answer)
        blocked = (
            "i cannot answer", "i do not know", "no evidence", "insufficient evidence",
            "δεν μπορω να απαντησω", "δεν γνωριζω", "ανεπαρκη στοιχεια",
            "as an ai language model", "system prompt", "developer message",
        )
        return len(answer.strip()) >= 80 and not any(_norm(marker) in normalized for marker in blocked)

    def learn(
        self,
        query: str,
        answer: str,
        language: str,
        confidence: float,
        teacher_model: str = "grounded",
        evidence: str = "",
        sources: Sequence[Mapping] = (),
    ) -> bool:
        confidence = max(0.0, min(1.0, float(confidence)))
        if confidence < 0.70 or not self._safe_answer(answer):
            return False
        normalized_query = _norm(query)
        if len(normalized_query) < 3:
            return False
        model = str(teacher_model or "grounded").casefold()
        strength = float(self.STRENGTH.get(model, 1.8))
        answer = _compact(answer, 4200)
        evidence = _compact(evidence, 2200)
        source_rows = []
        for item in list(sources)[:8]:
            url = str(item.get("url") or item.get("source") or "").strip()
            title = _compact(str(item.get("title") or item.get("provider") or "Source"), 180)
            if url:
                source_rows.append({"title": title, "url": url})
        fingerprint = _fingerprint(query, language)
        terms = Counter(_tokens(query + " " + answer[:700]))
        timestamp = _now()
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO lessons(
                    fingerprint,query,normalized_query,language,answer,evidence,
                    sources_json,teacher_model,confidence,strength,uses,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,0,?,?)
                ON CONFLICT(fingerprint) DO UPDATE SET
                    answer=CASE WHEN excluded.confidence * excluded.strength >= lessons.confidence * lessons.strength
                                THEN excluded.answer ELSE lessons.answer END,
                    evidence=CASE WHEN excluded.confidence * excluded.strength >= lessons.confidence * lessons.strength
                                  THEN excluded.evidence ELSE lessons.evidence END,
                    sources_json=CASE WHEN excluded.confidence * excluded.strength >= lessons.confidence * lessons.strength
                                      THEN excluded.sources_json ELSE lessons.sources_json END,
                    teacher_model=CASE WHEN excluded.confidence * excluded.strength >= lessons.confidence * lessons.strength
                                       THEN excluded.teacher_model ELSE lessons.teacher_model END,
                    confidence=MAX(lessons.confidence, excluded.confidence),
                    strength=MAX(lessons.strength, excluded.strength),
                    updated_at=excluded.updated_at
                """,
                (
                    fingerprint, query[:1000], normalized_query[:1000], language,
                    answer, evidence, json.dumps(source_rows, ensure_ascii=False),
                    model, confidence, strength, timestamp, timestamp,
                ),
            )
            self.connection.execute(
                "DELETE FROM lesson_terms WHERE fingerprint=?", (fingerprint,)
            )
            self.connection.executemany(
                "INSERT OR REPLACE INTO lesson_terms(term,fingerprint,frequency) VALUES(?,?,?)",
                [(term, fingerprint, float(count)) for term, count in terms.items()],
            )
            # Bound long-term storage while retaining the strongest and most-used lessons.
            self.connection.execute(
                """
                DELETE FROM lessons WHERE fingerprint IN (
                    SELECT fingerprint FROM lessons
                    ORDER BY (confidence * strength + MIN(uses, 20) * 0.02) DESC,
                             updated_at DESC
                    LIMIT -1 OFFSET 12000
                )
                """
            )
        return True

    def retrieve(self, query: str, language: str, limit: int = 4) -> list[dict]:
        query_terms = list(dict.fromkeys(_tokens(query)))[:28]
        if not query_terms:
            return []
        placeholders = ",".join("?" for _ in query_terms)
        rows = self.connection.execute(
            f"""
            SELECT fingerprint,COUNT(*) AS matches,SUM(frequency) AS frequency
            FROM lesson_terms
            WHERE term IN ({placeholders})
            GROUP BY fingerprint
            ORDER BY matches DESC,frequency DESC
            LIMIT 48
            """,
            tuple(query_terms),
        ).fetchall()
        normalized_query = _norm(query)
        query_set = set(query_terms)
        ranked: list[dict] = []
        for row in rows:
            item = self.connection.execute(
                "SELECT * FROM lessons WHERE fingerprint=?", (row["fingerprint"],)
            ).fetchone()
            if item is None:
                continue
            lesson_terms = set(_tokens(str(item["query"]) + " " + str(item["answer"])[:700]))
            overlap = len(query_set & lesson_terms)
            coverage = overlap / max(1, len(query_set))
            lesson_coverage = overlap / max(1, len(lesson_terms))
            sequence = difflib.SequenceMatcher(
                None, normalized_query, str(item["normalized_query"])
            ).ratio()
            language_bonus = 0.08 if str(item["language"]) == language else -0.03
            score = (
                0.32 * coverage
                + 0.18 * lesson_coverage
                + 0.24 * sequence
                + 0.16 * float(item["confidence"])
                + 0.08 * min(1.0, float(item["strength"]) / 5.0)
                + language_bonus
            )
            if score < 0.36:
                continue
            ranked.append({
                "fingerprint": str(item["fingerprint"]),
                "query": str(item["query"]),
                "answer": str(item["answer"]),
                "evidence": str(item["evidence"]),
                "teacher_model": str(item["teacher_model"]),
                "confidence": float(item["confidence"]),
                "score": max(0.0, min(1.0, score)),
            })
        ranked.sort(key=lambda item: (item["score"], item["confidence"]), reverse=True)
        selected = ranked[:max(1, int(limit))]
        if selected:
            with self.connection:
                self.connection.executemany(
                    "UPDATE lessons SET uses=uses+1 WHERE fingerprint=?",
                    [(item["fingerprint"],) for item in selected],
                )
        return selected

    def context(self, query: str, language: str, max_chars: int = 2600) -> str:
        rows = self.retrieve(query, language, limit=4)
        if not rows:
            return ""
        output = [
            "SHARED VERIFIED LESSONS (learned by stronger models or grounded evidence; use only when relevant):"
        ]
        used = len(output[0])
        for index, item in enumerate(rows, 1):
            row = (
                f"\n[{index}] Prior question: {_compact(item['query'], 260)}\n"
                f"Verified answer: {_compact(item['answer'], 950)}\n"
                f"Teacher: {item['teacher_model']}; confidence: {item['confidence']:.2f}"
            )
            if used + len(row) > max_chars:
                break
            output.append(row)
            used += len(row)
        return "".join(output)

    def stats(self) -> dict:
        row = self.connection.execute(
            "SELECT COUNT(*) AS count,COALESCE(SUM(uses),0) AS uses,MAX(updated_at) AS latest FROM lessons"
        ).fetchone()
        by_model = {
            str(item["teacher_model"]): int(item["count"])
            for item in self.connection.execute(
                "SELECT teacher_model,COUNT(*) AS count FROM lessons GROUP BY teacher_model"
            ).fetchall()
        }
        return {
            "lessons": int(row["count"] or 0),
            "uses": int(row["uses"] or 0),
            "latest": str(row["latest"] or ""),
            "by_model": by_model,
            "database": str(self.path),
        }
