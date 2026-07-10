"""Fast bilingual indexed knowledge retrieval shared by every Pocket AI model."""
from __future__ import annotations

import gzip
import json
import re
import sqlite3
import unicodedata
from pathlib import Path
from typing import Optional

MODULE_VERSION = 4

_STOP = {
    'the','a','an','of','is','are','was','were','be','been','do','does','did','what','which','who','tell','about','define','explain','please','meaning','means','mean','information','facts','fact','give',
    'της','τησ','του','των','η','ο','το','τι','ειναι','ποια','ποιο','ποιος','πες','μου','για','εξηγησε'
}


def _norm(value: str) -> str:
    value = unicodedata.normalize('NFKD', str(value).casefold())
    value = ''.join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r'[^0-9a-zα-ω]+', ' ', value)
    return re.sub(r'\s+', ' ', value).strip()


def _variants(value: str) -> list[str]:
    normalized=_norm(value)
    variants=[normalized]
    cleaned=re.sub(r'^(?:η|ο|το)\s+', '', normalized)
    cleaned=re.sub(r'^(?:πρωτευουσα|capital)\s+(?:τησ|του|of)\s+', '', cleaned)
    if cleaned and cleaned not in variants:
        variants.append(cleaned)
    words=cleaned.split()
    if words:
        last=words[-1]
        stems=[]
        if last.endswith('ασ') and len(last)>4:
            stems.append(last[:-1])
        if last.endswith('ησ') and len(last)>4:
            stems.append(last[:-1])
        if last.endswith('ου') and len(last)>4:
            stems.append(last[:-2])
        for stem in stems:
            candidate=' '.join(words[:-1]+[stem])
            if candidate not in variants:
                variants.append(candidate)
    return variants


def _tokens(value: str) -> list[str]:
    result=[]
    for token in _norm(value).split():
        if token in _STOP or len(token) <= 1:
            continue
        if token.endswith(('ς','σ')) and len(token) > 4:
            token=token[:-1]
        if token not in result:
            result.append(token)
    return result


class UniversalKnowledge:
    """SQLite FTS-backed retriever with a tiny gzip fallback for damaged installs."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.db_path = self.path.parent / 'PocketAI_Max_Knowledge.sqlite3'
        self.conn: Optional[sqlite3.Connection] = None
        self.entries=[]
        self.alias_map={}
        self.last_topic=''
        self.entry_count=0
        self.category_counts={}
        self._open_database()
        if self.conn is None:
            self._load_fallback()

    def _open_database(self) -> None:
        if not self.db_path.exists():
            return
        try:
            conn=sqlite3.connect(f'file:{self.db_path}?mode=ro', uri=True, check_same_thread=False)
            conn.row_factory=sqlite3.Row
            meta={row['key']:row['value'] for row in conn.execute('SELECT key,value FROM meta')}
            self.entry_count=int(meta.get('entry_count','0'))
            try:
                self.category_counts=json.loads(meta.get('categories','{}'))
            except Exception:
                self.category_counts={}
            self.conn=conn
        except Exception:
            self.conn=None

    def _load_fallback(self) -> None:
        try:
            with gzip.open(self.path,'rt',encoding='utf-8') as handle:
                data=json.load(handle)
            self.entries=list(data.get('entries',[])) if isinstance(data,dict) else []
        except Exception:
            self.entries=[]
        for idx,item in enumerate(self.entries):
            for alias in list(item.get('aliases',[]))+[item.get('id','')]:
                normalized=_norm(alias)
                if normalized:
                    self.alias_map.setdefault(normalized,idx)
        self.entry_count=len(self.entries)
        for item in self.entries:
            category=str(item.get('category','general'))
            self.category_counts[category]=self.category_counts.get(category,0)+1

    def _subject(self,text: str) -> tuple[str,bool]:
        normalized=_norm(text)
        prefixes=(
            'what is ','what are ','whats ','define ','explain ','explain the ','tell me about ','teach me about ',
            'who is ','who was ','value of ','capital of ','atomic number of ',
            'τι ειναι ','τι ηταν ','ποια ειναι ','ποιο ειναι ','ποιος ειναι ','ορισε ','εξηγησε ',
            'πες μου για ','μαθε μου για ','τιμη του ','τιμη της ','πρωτευουσα της ','πρωτευουσα του '
        )
        for prefix in prefixes:
            if normalized.startswith(prefix):
                return normalized[len(prefix):].strip(), True
        return normalized, len(normalized.split()) <= 7

    def _row_result(self,row,language: str,route: str,score: float) -> dict:
        self.last_topic=str(row['id'])
        grades=[int(x) for x in str(row['grades']).split(',') if x.isdigit()]
        return {
            'response':str(row['el'] if language=='el' else row['en']),
            'route':route,
            'knowledge_id':self.last_topic,
            'category':str(row['category']),
            'match_score':score,
            'grades':grades,
        }

    def _db_exact(self,subject: str):
        return self.conn.execute(
            'SELECT e.* FROM aliases a JOIN entries e ON e.id=a.entry_id '
            'WHERE a.normalized=? ORDER BY e.priority DESC LIMIT 1',(subject,)
        ).fetchone()

    def _fts_rows(self,text: str,limit: int=8):
        tokens=_tokens(text)[:12]
        if not tokens:
            return []
        query=' OR '.join('"'+t.replace('"','')+'"' for t in tokens)
        try:
            return self.conn.execute(
                'SELECT e.*, bm25(knowledge_fts, 0.0, 6.0, 1.5, 1.5, 0.4) AS rank '
                'FROM knowledge_fts JOIN entries e ON e.id=knowledge_fts.entry_id '
                'WHERE knowledge_fts MATCH ? ORDER BY rank, e.priority DESC LIMIT ?',
                (query,limit)
            ).fetchall()
        except sqlite3.Error:
            return []

    def answer(self,text: str,language: str='en') -> Optional[dict]:
        subject,definition_like=self._subject(text)
        subject=re.sub(r'^(?:a|an|the|ενα|ενας|μια|το|η|ο)\s+','',subject).strip()
        if self.conn is not None:
            variants=_variants(subject)
            row=None
            capital_intent=('capital' in _norm(text) or 'πρωτευουσα' in _norm(text))
            for variant in variants:
                if capital_intent:
                    for prefix in ('capital of ', 'πρωτευουσα ', 'πρωτεύουσα '):
                        row=self._db_exact(_norm(prefix+variant))
                        if row is not None:
                            break
                if row is None:
                    row=self._db_exact(variant)
                if row is not None:
                    break
            if row is not None:
                return self._row_result(row,language,'universal_knowledge',1.0)
            if definition_like:
                search_subject=variants[-1] if variants else subject
                query_tokens=set(_tokens(search_subject))
                for row in self._fts_rows(search_subject,8):
                    candidate_tokens=set(_tokens(' '.join((row['id'],row['category'],row['en'],row['el']))))
                    overlap=len(query_tokens & candidate_tokens)
                    coverage=overlap/max(1,len(query_tokens))
                    if coverage >= 0.66 or (len(query_tokens)==1 and overlap==1):
                        return self._row_result(row,language,'universal_knowledge_indexed',min(0.97,0.64+coverage*0.30))
            return None

        idx=self.alias_map.get(subject)
        if idx is None:
            return None
        item=self.entries[idx]
        self.last_topic=str(item.get('id',''))
        return {
            'response':str(item.get('el' if language=='el' else 'en','')),
            'route':'universal_knowledge_fallback','knowledge_id':self.last_topic,
            'category':str(item.get('category','general')),'match_score':1.0,'grades':item.get('grades',[])
        }

    def context(self,text: str,language: str='en',limit: int=6,max_chars: int=2800) -> str:
        """Return compact, query-overlapping facts for injection into any model."""
        if self.conn is None:
            found=self.answer(text,language)
            return found['response'] if found else ''
        query_tokens=set(_tokens(text))
        if not query_tokens:
            return ''
        normalized=_norm(text)
        technical_cues={
            'python','code','function','method','module','library','api','matplotlib','programming',
            'javascript','java','c++','sql','κωδικ','συναρτηση','βιβλιοθηκ','προγραμματισ'
        }
        technical_query=any(cue in normalized for cue in technical_cues)
        rows=self._fts_rows(text,max(12,limit*5))
        ranked=[]
        used=set()
        for row in rows:
            item_id=str(row['id'])
            if item_id in used:
                continue
            used.add(item_id)
            category=str(row['category'])
            technical_item=item_id.startswith('py_') or category.endswith('_reference')
            if technical_item and not technical_query:
                continue
            candidate_tokens=set(_tokens(' '.join((item_id,category,str(row['en']),str(row['el'])))))
            overlap=len(query_tokens & candidate_tokens)
            coverage=overlap/max(1,len(query_tokens))
            if overlap < 1 or coverage < (0.45 if len(query_tokens)>1 else 1.0):
                continue
            exact_bonus=0.2 if _norm(item_id) in normalized or normalized in _norm(str(row['en'])) else 0.0
            rank_value=abs(float(row['rank'] or 0.0))
            rank_quality=1.0/(1.0+rank_value)
            score=coverage+exact_bonus+0.08*rank_quality
            ranked.append((score,row))
        ranked.sort(key=lambda pair:-pair[0])
        pieces=[]
        total=0
        for _,row in ranked:
            fact=str(row['el'] if language=='el' else row['en']).strip()
            if not fact:
                continue
            line=f'- {fact}'
            if total+len(line)>max_chars:
                break
            pieces.append(line)
            total+=len(line)+1
            if len(pieces)>=limit:
                break
        return '\n'.join(pieces)

    def answer_topic(self,topic_id: str,language: str='en') -> Optional[dict]:
        if self.conn is not None:
            row=self.conn.execute('SELECT * FROM entries WHERE id=?',(topic_id,)).fetchone()
            return self._row_result(row,language,'universal_followup',1.0) if row else None
        for item in self.entries:
            if item.get('id')==topic_id:
                return {'response':str(item.get('el' if language=='el' else 'en','')),
                        'route':'universal_followup','knowledge_id':topic_id,
                        'category':item.get('category','general'),'match_score':1.0}
        return None

    def catalog(self,language: str='en') -> str:
        top=sorted(self.category_counts.items(), key=lambda pair:(-pair[1],pair[0]))[:16]
        pairs=', '.join(f'{name}: {count}' for name,count in top)
        if language=='el':
            return f'Μέγιστη κοινή βάση γνώσης: {self.entry_count:,} εγγραφές με γρήγορη ευρετηρίαση. Κύριες κατηγορίες: {pairs}.'
        return f'Max shared knowledge foundation: {self.entry_count:,} indexed entries. Leading categories: {pairs}.'

    def close(self) -> None:
        if self.conn is not None:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn=None
