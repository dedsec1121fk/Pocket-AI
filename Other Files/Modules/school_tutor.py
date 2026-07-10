#!/usr/bin/env python3
"""Shared bilingual grade 1-12 school tutor for Pocket AI.

The module uses only Python's standard library. It provides deterministic math
solvers and a detailed bilingual grade-adapted curriculum knowledge database. It runs before any
optional GGUF model, so every hardware/model profile receives the same basic
school capabilities.
"""
from __future__ import annotations
import ast, difflib, gzip, json, math, re, sqlite3, statistics, unicodedata
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SPACE_RE=re.compile(r"\s+")

def stem_terms(text:str)->set[str]:
    result=set()
    endings=('ιων','ουσ','εων','ων','εισ','εσ','οι','οσ','ου','ησ','η','ασ','α','ια','ιο','ι')
    for token in norm(text).split():
        stem=token
        if re.fullmatch(r'[α-ω]+',token) and len(token)>=5:
            for ending in endings:
                if token.endswith(ending) and len(token)-len(ending)>=3:
                    stem=token[:-len(ending)]; break
        result.add(stem)
    return result

def norm(text:str)->str:
    text=unicodedata.normalize('NFD',text.casefold())
    text=''.join(c for c in text if unicodedata.category(c)!='Mn')
    text=text.replace('ς','σ').replace('×','*').replace('÷','/').replace('−','-').replace('²','^2')
    return SPACE_RE.sub(' ',re.sub(r'[^a-z0-9α-ωάέήίόύώϊϋΐΰ.+\-*/^=,%() ]+',' ',text)).strip()

class _Poly:
    @staticmethod
    def add(a,b,sign=1):
        out=dict(a)
        for k,v in b.items(): out[k]=out.get(k,0.0)+sign*v
        return {k:v for k,v in out.items() if abs(v)>1e-12}
    @staticmethod
    def mul(a,b):
        out={}
        for da,ca in a.items():
            for db,cb in b.items():
                d=da+db
                if d>2: raise ValueError('degree above 2')
                out[d]=out.get(d,0.0)+ca*cb
        return out
    @classmethod
    def parse(cls,expr:str)->Dict[int,float]:
        expr=expr.replace('^','**')
        tree=ast.parse(expr,mode='eval')
        def walk(n):
            if isinstance(n,ast.Expression): return walk(n.body)
            if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)): return {0:float(n.value)}
            if isinstance(n,ast.Name) and n.id.casefold()=='x': return {1:1.0}
            if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.UAdd,ast.USub)):
                p=walk(n.operand); return p if isinstance(n.op,ast.UAdd) else {d:-c for d,c in p.items()}
            if isinstance(n,ast.BinOp):
                a,b=walk(n.left),walk(n.right)
                if isinstance(n.op,ast.Add): return cls.add(a,b)
                if isinstance(n.op,ast.Sub): return cls.add(a,b,-1)
                if isinstance(n.op,ast.Mult): return cls.mul(a,b)
                if isinstance(n.op,ast.Div):
                    if set(b)-{0} or abs(b.get(0,0))<1e-12: raise ValueError('division must be by a nonzero constant')
                    return {d:c/b[0] for d,c in a.items()}
                if isinstance(n.op,ast.Pow):
                    if set(b)-{0}: raise ValueError('invalid power')
                    power=int(b.get(0,0))
                    if power not in (0,1,2): raise ValueError('power must be 0, 1, or 2')
                    out={0:1.0}
                    for _ in range(power): out=cls.mul(out,a)
                    return out
            raise ValueError('unsupported expression')
        return walk(tree)

GRADE_TRANSLATIONS = {
    'counting and place value':'μέτρηση και αξία θέσης', 'addition and subtraction':'πρόσθεση και αφαίρεση',
    'early multiplication/division':'εισαγωγή σε πολλαπλασιασμό και διαίρεση', 'shapes, time, money, and measurement':'σχήματα, χρόνος, χρήματα και μετρήσεις',
    'reading fluency':'ευχέρεια ανάγνωσης', 'spelling':'ορθογραφία', 'complete sentences':'ολοκληρωμένες προτάσεις', 'nouns, verbs, and simple paragraphs':'ουσιαστικά, ρήματα και απλές παράγραφοι',
    'living and nonliving things':'ζωντανά και μη ζωντανά', 'plants and animals':'φυτά και ζώα', 'weather, materials, and the Solar System':'καιρός, υλικά και Ηλιακό Σύστημα',
    'family and community':'οικογένεια και κοινότητα', 'maps and directions':'χάρτες και κατευθύνσεις', 'basic geography and timelines':'βασική γεωγραφία και χρονογραμμές',
    'safe device use':'ασφαλής χρήση συσκευών', 'hardware and software basics':'βασικά υλικού και λογισμικού', 'simple step-by-step algorithms':'απλοί αλγόριθμοι βήμα προς βήμα',
    'fractions and decimals':'κλάσματα και δεκαδικοί', 'percentages and ratios':'ποσοστά και λόγοι', 'factors and multiples':'παράγοντες και πολλαπλάσια', 'area, perimeter, volume, data, and probability':'εμβαδόν, περίμετρος, όγκος, δεδομένα και πιθανότητες',
    'grammar and verb tenses':'γραμματική και χρόνοι ρημάτων', 'paragraph and essay structure':'δομή παραγράφου και έκθεσης', 'vocabulary, summaries, and reading evidence':'λεξιλόγιο, περιλήψεις και τεκμήρια από κείμενο',
    'ecosystems and cells':'οικοσυστήματα και κύτταρα', 'matter and energy':'ύλη και ενέργεια', 'forces, circuits, Earth and space':'δυνάμεις, κυκλώματα, Γη και διάστημα',
    'physical and human geography':'φυσική και ανθρωπογεωγραφία', 'ancient civilizations':'αρχαίοι πολιτισμοί', 'citizenship and historical evidence':'ιδιότητα πολίτη και ιστορικά τεκμήρια',
    'algorithms':'αλγόριθμοι', 'digital literacy':'ψηφιακός γραμματισμός', 'introductory programming concepts':'εισαγωγικές έννοιες προγραμματισμού',
    'integers and exponents':'ακέραιοι και δυνάμεις', 'algebra and linear equations':'άλγεβρα και γραμμικές εξισώσεις', 'geometry and Pythagorean theorem':'γεωμετρία και Πυθαγόρειο θεώρημα', 'statistics and probability':'στατιστική και πιθανότητες',
    'advanced grammar':'προχωρημένη γραμματική', 'argument and evidence':'επιχείρημα και τεκμήρια', 'literary devices':'λογοτεχνικά σχήματα', 'research and source evaluation':'έρευνα και αξιολόγηση πηγών',
    'atoms and periodic table':'άτομα και περιοδικός πίνακας', 'cells, genetics, and ecosystems':'κύτταρα, γενετική και οικοσυστήματα', 'motion, energy, electricity, waves, and Earth systems':'κίνηση, ενέργεια, ηλεκτρισμός, κύματα και συστήματα της Γης',
    'medieval and early modern history':'μεσαιωνική και πρώιμη νεότερη ιστορία', 'geography and population':'γεωγραφία και πληθυσμός', 'democracy, civics, and economics':'δημοκρατία, αγωγή πολίτη και οικονομικά',
    'variables, conditions, loops, functions':'μεταβλητές, συνθήκες, βρόχοι και συναρτήσεις', 'debugging':'αποσφαλμάτωση', 'online safety and source reliability':'ασφάλεια στο διαδίκτυο και αξιοπιστία πηγών',
    'functions and quadratics':'συναρτήσεις και εξισώσεις δευτέρου βαθμού', 'trigonometry and vectors':'τριγωνομετρία και διανύσματα', 'statistics':'στατιστική', 'introductory limits, derivatives, and integrals':'εισαγωγή σε όρια, παραγώγους και ολοκληρώματα',
    'academic essays':'ακαδημαϊκές εκθέσεις', 'argumentation and rhetoric':'επιχειρηματολογία και ρητορική', 'literature analysis':'ανάλυση λογοτεχνίας', 'research writing and citation':'ερευνητική γραφή και παραπομπές',
    'mechanics, waves, electricity, and energy':'μηχανική, κύματα, ηλεκτρισμός και ενέργεια', 'chemistry, reactions, acids and bases':'χημεία, αντιδράσεις, οξέα και βάσεις', 'genetics, evolution, ecology, and human biology':'γενετική, εξέλιξη, οικολογία και ανθρώπινη βιολογία',
    'modern and world history':'νεότερη και παγκόσμια ιστορία', 'political institutions':'πολιτικοί θεσμοί', 'economics':'οικονομικά', 'philosophy and logic':'φιλοσοφία και λογική',
    'algorithms and data structures':'αλγόριθμοι και δομές δεδομένων', 'program design':'σχεδιασμός προγραμμάτων', 'testing, debugging, and digital ethics':'έλεγχος, αποσφαλμάτωση και ψηφιακή ηθική'
}

class SchoolTutor:
    def __init__(self, knowledge_path:Path):
        self.path=Path(knowledge_path)
        self.pack={'topics':[],'grades':{},'topic_count':0,'grade_lesson_count':0}
        try:
            with gzip.open(self.path,'rt',encoding='utf-8') as f: self.pack=json.load(f)
        except Exception: pass
        self.alias=[]
        for item in self.pack.get('topics',[]):
            for field in ('title_en','title_el'):
                value=norm(str(item.get(field,'')))
                if value: self.alias.append((value,item))
            for a in item.get('aliases',[]):
                value=norm(str(a))
                if value: self.alias.append((value,item))
        self.curriculum_path=self.path.parent/'School Knowledge'/'PocketAI_School_Curriculum.sqlite3'
        self.curriculum=None
        try:
            if self.curriculum_path.is_file():
                uri=f"file:{self.curriculum_path.as_posix()}?mode=ro&immutable=1"
                self.curriculum=sqlite3.connect(uri,uri=True,check_same_thread=False)
                self.curriculum.row_factory=sqlite3.Row
        except sqlite3.Error:
            self.curriculum=None
        self.topic_count=int(self.pack.get('topic_count') or len(self.pack.get('topics',[])))
        self.grade_lesson_count=int(self.pack.get('grade_lesson_count') or 0)
        if self.curriculum is not None:
            try:
                row=self.curriculum.execute("SELECT value FROM metadata WHERE key='grade_lesson_count'").fetchone()
                if row: self.grade_lesson_count=int(row[0])
            except Exception: pass
        self.last_topic=''
        self.last_grade=None
        self.last_depth='standard'

    def close(self)->None:
        try:
            if self.curriculum is not None: self.curriculum.close()
        except sqlite3.Error: pass
        self.curriculum=None

    @staticmethod
    def _detect_depth(text:str)->str:
        n=norm(text)
        deep=('in detail','detailed','deep explanation','full lesson','everything about','complete explanation','step by step','comprehensive','αναλυτικα','λεπτομερως','σε βαθος','πληρες μαθημα','ολα για','βημα βημα','ολοκληρωμενα')
        simple=('simple','simply','easy words','for a child','short answer','briefly','απλα','με απλα λογια','σαν παιδι','συντομα','περιληπτικα')
        if any(cue in n for cue in deep): return 'detailed'
        if any(cue in n for cue in simple): return 'simple'
        return 'standard'

    @staticmethod
    def _detect_grade(text:str)->Optional[int]:
        n=norm(text)
        m=re.search(r'\b(?:grade|class|year|ταξη)\s*(1[0-2]|[1-9])\b',n)
        if m: return int(m.group(1))
        m=re.search(r'\b(1[0-2]|[1-9])(?:st|nd|rd|th)?\s*(?:grade|class|year)\b',n)
        if m: return int(m.group(1))
        greek_letter={'α':1,'β':2,'γ':3,'δ':4,'ε':5,'στ':6}
        for level,offset,max_local in (('δημοτικ',0,6),('γυμνασι',6,3),('λυκει',9,3)):
            gm=re.search(r'\b(στ|α|β|γ|δ|ε)\s*'+level,n)
            if gm:
                local=greek_letter.get(gm.group(1),0)
                if 1<=local<=max_local: return offset+local
        return None

    @staticmethod
    def _subject_alias(subject:str)->str:
        key=norm(subject)
        aliases={'mathematics':'math','maths':'math','math':'math','μαθηματικα':'math','science':'science','επιστημη':'science','επιστημες':'science','φυσικες επιστημες':'science','language':'language','english':'language','greek':'language','γλωσσα':'language','αγγλικα':'language','ελληνικα':'language','history':'humanities','humanities':'humanities','social studies':'humanities','ιστορια':'humanities','κοινωνικες επιστημες':'humanities','geography':'geography','γεωγραφια':'geography','computing':'computing','computer science':'computing','πληροφορικη':'computing','health':'health','life skills':'health','υγεια':'health','δεξιοτητες ζωης':'health','arts':'arts','art':'arts','music':'arts','τεχνες':'arts','μουσικη':'arts','economics':'economics','civics':'economics','οικονομικα':'economics','αγωγη πολιτη':'economics'}
        key=re.sub(r'\b(?:topics?|subjects?|curriculum|lessons?|θεματα|μαθηματα|υλη|κεφαλαια)\b',' ',key).strip()
        return aliases.get(key,key)

    def _db_search(self,text:str,grade:Optional[int]=None,subject:str='',limit:int=5)->List[dict]:
        if self.curriculum is None: return []
        stop={'what','is','are','explain','teach','me','about','the','for','grade','class','year','please','τι','ειναι','εξηγησε','μαθε','μου','για','την','ταξη','παρακαλω','detail','detailed','αναλυτικα'}
        terms=[term for term in norm(text).split() if len(term)>1 and term not in stop]
        if not terms: return []
        match=' OR '.join('"'+term.replace('"','')+'"' for term in terms[:12])
        conditions=[]; params=[]
        if grade is not None:
            conditions.append('? BETWEEN l.grade_min AND l.grade_max'); params.append(int(grade))
        subject_key=self._subject_alias(subject) if subject else ''
        if subject_key:
            conditions.append('l.subject=?'); params.append(subject_key)
        where=(' AND '+' AND '.join(conditions)) if conditions else ''
        sql=("SELECT l.*,bm25(lessons_fts,7.0,7.0,4.5,2.0,2.0,1.1,1.1,0.4,0.4) rank FROM lessons_fts JOIN lessons l ON l.id=lessons_fts.rowid WHERE lessons_fts MATCH ?"+where+" ORDER BY rank LIMIT ?")
        try: rows=self.curriculum.execute(sql,[match,*params,int(limit)]).fetchall()
        except sqlite3.Error: return []
        return [dict(row) for row in rows]

    def _grade_lesson(self,topic_id:str,grade:Optional[int])->Optional[dict]:
        if self.curriculum is None or not topic_id: return None
        if grade is None:
            try:
                row=self.curriculum.execute('SELECT grade_min,grade_max FROM lessons WHERE topic_id=?',(topic_id,)).fetchone()
                grade=int(round((row['grade_min']+row['grade_max'])/2)) if row else 7
            except Exception: grade=7
        try:
            row=self.curriculum.execute('SELECT * FROM grade_lessons WHERE topic_id=? AND grade=? LIMIT 1',(topic_id,int(grade))).fetchone()
            if row is None:
                row=self.curriculum.execute('SELECT * FROM grade_lessons WHERE topic_id=? ORDER BY abs(grade-?) LIMIT 1',(topic_id,int(grade))).fetchone()
            return dict(row) if row else None
        except sqlite3.Error: return None

    def _format_lesson(self,item:dict,language:str,depth:str,grade:Optional[int])->str:
        suffix='el' if language=='el' else 'en'
        title=str(item.get('title_el' if language=='el' else 'title_en') or item.get('title_en') or '').strip()
        lesson=self._grade_lesson(str(item.get('topic_id') or ''),grade)
        if lesson:
            stored_grade=int(lesson.get('grade') or grade or 7)
            if grade is not None and int(grade)!=stored_grade:
                adapted={}
                for key,value in lesson.items():
                    if isinstance(value,str):
                        value=re.sub(rf'grade[- ]{stored_grade}\b',f'grade-{int(grade)}',value,flags=re.I)
                        value=re.sub(rf'τάξη\s+{stored_grade}\b',f'τάξη {int(grade)}',value,flags=re.I)
                    adapted[key]=value
                lesson=adapted
            core=str(lesson.get(f'core_explanation_{suffix}') or item.get(f'summary_{suffix}') or '').strip()
            if depth=='simple': return f"{title}: {core}"
            if depth=='standard':
                example=str(lesson.get(f'worked_example_{suffix}') or '').strip()
                misconception=str(lesson.get(f'misconception_{suffix}') or '').strip()
                return '\n\n'.join(x for x in (f"{title}\n{core}",example,misconception) if x)
            labels_el=('Μαθησιακός στόχος','Προαπαιτούμενα','Βασική εξήγηση','Τρόπος κατανόησης','Λεξιλόγιο','Καθοδηγούμενο παράδειγμα','Συνηθισμένο λάθος','Εξάσκηση','Έλεγχος κατάκτησης','Σχετικά θέματα','Τοπικά τεκμήρια')
            labels_en=('Learning goal','Prerequisites','Core explanation','How to learn it','Vocabulary','Guided example','Common misconception','Practice','Mastery check','Related topics','Local evidence')
            labels=labels_el if language=='el' else labels_en
            fields=('learning_goal','prior_knowledge','core_explanation','teaching_strategy','vocabulary','worked_example','misconception','practice','mastery_check','related_topics','evidence')
            parts=[title]
            for label,field in zip(labels,fields):
                value=str(lesson.get(f'{field}_{suffix}') or '').strip()
                if value: parts.append(f"{label}: {value}")
            return '\n\n'.join(parts)
        summary=str(item.get(f'summary_{suffix}') or item.get('summary_en') or '').strip()
        details=str(item.get(f'details_{suffix}') or item.get('details_en') or '').strip()
        return f"{title}: {details if depth=='detailed' and details else summary}"
    def _fmt(value:float)->str:
        if abs(value-round(value))<1e-10: return str(int(round(value)))
        return f'{value:.10g}'
    @staticmethod
    def _safe_number_expr(expr:str)->float:
        tree=ast.parse(expr.replace('^','**'),mode='eval')
        def w(n):
            if isinstance(n,ast.Expression): return w(n.body)
            if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)): return float(n.value)
            if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.UAdd,ast.USub)): return w(n.operand) if isinstance(n.op,ast.UAdd) else -w(n.operand)
            if isinstance(n,ast.BinOp) and isinstance(n.op,(ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Pow,ast.Mod)):
                a,b=w(n.left),w(n.right)
                if isinstance(n.op,ast.Add): return a+b
                if isinstance(n.op,ast.Sub): return a-b
                if isinstance(n.op,ast.Mult): return a*b
                if isinstance(n.op,ast.Div): return a/b
                if isinstance(n.op,ast.Pow):
                    if abs(b)>12 or abs(a)>1e9: raise ValueError('power too large')
                    return a**b
                return a%b
            raise ValueError('unsupported arithmetic')
        value=w(tree)
        if not math.isfinite(value): raise ValueError('non-finite result')
        return value
    def grade_overview(self,grade:int,subject:str,language:str)->str:
        if not 1<=int(grade)<=12: return ''
        subject_key=self._subject_alias(subject) if subject else ''
        labels_en={'math':'Mathematics','language':'Language and literature','science':'Science','humanities':'History and humanities','geography':'Geography','computing':'Computing','health':'Health and life skills','arts':'Arts and music','economics':'Economics and civics'}
        labels_el={'math':'Μαθηματικά','language':'Γλώσσα και λογοτεχνία','science':'Φυσικές επιστήμες','humanities':'Ιστορία και ανθρωπιστικές επιστήμες','geography':'Γεωγραφία','computing':'Πληροφορική','health':'Υγεία και δεξιότητες ζωής','arts':'Τέχνες και μουσική','economics':'Οικονομικά και αγωγή του πολίτη'}
        rows=[]
        if self.curriculum is not None:
            try:
                if subject_key:
                    rows=self.curriculum.execute('SELECT DISTINCT l.subject,l.title_en,l.title_el FROM grade_lessons g JOIN lessons l ON l.topic_id=g.topic_id WHERE g.grade=? AND l.subject=? ORDER BY l.title_en LIMIT 24',(int(grade),subject_key)).fetchall()
                else:
                    rows=self.curriculum.execute('SELECT DISTINCT l.subject,l.title_en,l.title_el FROM grade_lessons g JOIN lessons l ON l.topic_id=g.topic_id WHERE g.grade=? ORDER BY l.subject,l.title_en',(int(grade),)).fetchall()
            except sqlite3.Error: rows=[]
        if not rows: return ''
        groups={}
        for row in rows: groups.setdefault(row['subject'],[]).append(row['title_el'] if language=='el' else row['title_en'])
        title=(f'Αναλυτικός χάρτης γνώσεων για την τάξη {grade}' if language=='el' else f'Detailed knowledge map for grade {grade}')
        lines=[title]
        labels=labels_el if language=='el' else labels_en
        for key,values in groups.items(): lines.append(f"- {labels.get(key,key.title())}: "+'; '.join(values[:18]))
        return '\n'.join(lines)
    def _math(self,text:str,language:str)->Optional[dict]:
        n=norm(text); label='Αποτέλεσμα' if language=='el' else 'Result'
        # Percent of
        m=re.search(r'(-?\d+(?:[.,]\d+)?)\s*%\s*(?:of|του|απο)\s*(-?\d+(?:[.,]\d+)?)',n)
        if m:
            p=float(m.group(1).replace(',','.')); x=float(m.group(2).replace(',','.')); v=p*x/100
            return {'response':f'{label}: {self._fmt(v)} ({self._fmt(p)}% × {self._fmt(x)})','route':'school_math_percentage'}
        # Fractions operation
        m=re.search(r'(-?\d+)\s*/\s*(\d+)\s*([+\-*/])\s*(-?\d+)\s*/\s*(\d+)',n)
        if m:
            a=Fraction(int(m.group(1)),int(m.group(2))); b=Fraction(int(m.group(4)),int(m.group(5))); op=m.group(3)
            v={'+':lambda:a+b,'-':lambda:a-b,'*':lambda:a*b,'/':lambda:a/b}[op]()
            dec=float(v)
            return {'response':f'{label}: {v.numerator}/{v.denominator}' + (f' = {self._fmt(dec)}' if v.denominator!=1 else ''),'route':'school_math_fraction'}
        # mean/median/mode/range
        sm=re.search(r'\b(mean|average|median|mode|range|μεσος ορος|διαμεσος|επικρατουσα τιμη|ευρος)\b(?:\s+of|\s+των|\s*:)?\s*([\d.,\s\-]+)',n)
        if sm:
            vals=[float(x.replace(',','.')) for x in re.findall(r'-?\d+(?:[.,]\d+)?',sm.group(2))]
            if vals:
                kind=sm.group(1)
                if kind in {'mean','average','μεσος ορος'}: v=sum(vals)/len(vals)
                elif kind in {'median','διαμεσος'}: v=statistics.median(vals)
                elif kind in {'range','ευρος'}: v=max(vals)-min(vals)
                else:
                    counts=Counter(vals); high=max(counts.values()); modes=[x for x,c in counts.items() if c==high]
                    return {'response':f'{label}: '+', '.join(self._fmt(x) for x in sorted(modes)),'route':'school_math_statistics'}
                return {'response':f'{label}: {self._fmt(v)}','route':'school_math_statistics'}
        # gcd/lcm
        gm=re.search(r'\b(gcd|hcf|lcm|μκδ|μκδ|εκπ|mcd|ekp)\b[^\d]*(\d+)[^\d]+(\d+)',n)
        if gm:
            a,b=int(gm.group(2)),int(gm.group(3)); kind=gm.group(1)
            v=math.gcd(a,b) if kind in {'gcd','hcf','μκδ','mcd'} else abs(a*b)//math.gcd(a,b)
            return {'response':f'{label}: {v}','route':'school_math_number_theory'}
        # geometry rectangle/triangle/circle
        rect=re.search(r'(?:area|εμβαδον).*(?:rectangle|ορθογωνι).*(?:length|μηκος)\s*[=:]?\s*(\d+(?:[.,]\d+)?).*(?:width|πλατος)\s*[=:]?\s*(\d+(?:[.,]\d+)?)',n)
        if rect:
            a=float(rect.group(1).replace(',','.')); b=float(rect.group(2).replace(',','.'))
            return {'response':f"{label}: {self._fmt(a*b)} {'τετραγωνικές μονάδες' if language=='el' else 'square units'}",'route':'school_math_geometry'}
        tri=re.search(r'(?:area|εμβαδον).*(?:triangle|τριγων).*(?:base|βαση)\s*[=:]?\s*(\d+(?:[.,]\d+)?).*(?:height|υψος)\s*[=:]?\s*(\d+(?:[.,]\d+)?)',n)
        if tri:
            b=float(tri.group(1).replace(',','.')); h=float(tri.group(2).replace(',','.'))
            return {'response':f"{label}: {self._fmt(b*h/2)} {'τετραγωνικές μονάδες' if language=='el' else 'square units'}",'route':'school_math_geometry'}
        circ=re.search(r'(?:area|εμβαδον|circumference|περιφερεια).*(?:circle|κυκλ).*(?:radius|ακτινα)\s*[=:]?\s*(\d+(?:[.,]\d+)?)',n)
        if circ:
            r=float(circ.group(1).replace(',','.')); is_area=('area' in n or 'εμβαδον' in n); v=math.pi*r*r if is_area else 2*math.pi*r
            return {'response':f"{label}: {self._fmt(v)} " + (('τετραγωνικές μονάδες' if language=='el' else 'square units') if is_area else ('μονάδες' if language=='el' else 'units')),'route':'school_math_geometry'}
        # equations. Require an equals sign and x.
        if 'x' in n and '=' in n:
            eq=n
            eq=re.sub(r'^(?:solve|solve for x|λυσε|λυσε για x)\s*','',eq)
            eq=re.sub(r'(?<=\d)x', '*x', eq)
            eq=re.sub(r'x(?=\d)', 'x*', eq)
            eq=re.sub(r'(?<=\))x', '*x', eq)
            eq=re.sub(r'x(?=\()', 'x*', eq)
            try:
                left,right=eq.split('=',1); poly=_Poly.add(_Poly.parse(left),_Poly.parse(right),-1)
                a=poly.get(2,0.0); b=poly.get(1,0.0); c=poly.get(0,0.0)
                if abs(a)<1e-12:
                    if abs(b)<1e-12:
                        response=('Every real x is a solution.' if abs(c)<1e-12 else 'There is no solution.') if language!='el' else ('Κάθε πραγματικός x είναι λύση.' if abs(c)<1e-12 else 'Δεν υπάρχει λύση.')
                    else: response=f'x = {self._fmt(-c/b)}'
                    return {'response':response,'route':'school_math_linear_equation'}
                disc=b*b-4*a*c
                if disc<0:
                    response=('No real roots. Complex roots: ' if language!='el' else 'Δεν υπάρχουν πραγματικές ρίζες. Μιγαδικές ρίζες: ')
                    re_part=-b/(2*a); im=math.sqrt(-disc)/(2*abs(a)); response+=f'{self._fmt(re_part)} ± {self._fmt(im)}i'
                else:
                    s=math.sqrt(disc); roots=[(-b+s)/(2*a),(-b-s)/(2*a)]
                    response='x = '+', '.join(dict.fromkeys(self._fmt(v) for v in roots))
                return {'response':response,'route':'school_math_quadratic_equation'}
            except Exception: pass
        # Natural arithmetic without requiring calc.
        q=n
        prefixes=('what is ','calculate ','compute ','how much is ','ποσο κανει ','υπολογισε ','βρες ')
        for p in prefixes:
            if q.startswith(p): q=q[len(p):].strip(); break
        q=q.rstrip('? ')
        if re.fullmatch(r'[0-9.,+\-*/^()% ]{3,}',q) and any(ch in q for ch in '+-*/^'):
            try:
                expr=q.replace(',','.').replace('%','/100')
                v=self._safe_number_expr(expr)
                return {'response':f'{label}: {self._fmt(v)}','route':'school_math_arithmetic'}
            except Exception: pass
        return None
    def _topic(self,text:str,language:str,grade:Optional[int]=None,depth:str='standard')->Optional[dict]:
        n=norm(text)
        query_terms=stem_terms(n)
        best=None
        for alias,item in self.alias:
            if not alias: continue
            alias_terms=stem_terms(alias)
            overlap=len(query_terms & alias_terms)
            coverage=overlap/max(1,len(alias_terms))
            contains=1.0 if alias in n else 0.0
            exact=1.0 if n==alias else 0.0
            length_bonus=min(0.12,len(alias)/120) if contains else 0.0
            score=0.52*coverage+0.30*contains+0.12*exact+length_bonus
            if best is None or score>best[0]: best=(score,item,alias)
        rows=[]
        if best and best[0]>=0.50 and self.curriculum is not None:
            try:
                row=self.curriculum.execute('SELECT * FROM lessons WHERE topic_id=? LIMIT 1',(str(best[1].get('id') or ''),)).fetchone()
                if row is not None: rows=[dict(row)]
            except sqlite3.Error: rows=[]
        if not rows: rows=self._db_search(text,grade=grade,limit=5)
        if rows:
            item=rows[0]
            answer=self._format_lesson(item,language,depth,grade)
            self.last_topic=str(item.get('title_el' if language=='el' else 'title_en') or item.get('title_en') or '')
            self.last_grade=grade; self.last_depth=depth
            return {'response':answer,'route':'school_knowledge','subject':item.get('subject'),'grades':[item.get('grade_min'),item.get('grade_max')],'topic':item.get('topic_id'),'match':float(best[0] if best else item.get('rank',0.0)),'requires_generation':language=='el' and bool(item.get('evidence')),'school_evidence':item.get('evidence','')}
        if best and best[0]>=0.48:
            item=best[1]; response=item.get('summary_el' if language=='el' else 'summary_en','')
            return {'response':response,'route':'school_knowledge','subject':item.get('subject'),'grades':[item.get('grade_min'),item.get('grade_max')],'topic':item.get('id'),'match':best[0]}
        return None
    def answer(self,text:str,language:str='en')->Optional[dict]:
        n=norm(text); depth=self._detect_depth(text); grade=self._detect_grade(text)
        full_catalog=('all school knowledge','everything from grade 1 to 12','complete school curriculum','first to last grade','ολη η σχολικη γνωση','ολα απο την πρωτη μεχρι την τελευταια ταξη','πληρες σχολικο προγραμμα')
        if n in {'school help','help with school','school tutor','σχολικη βοηθεια','βοηθεια για σχολειο','σχολικος βοηθος'} or any(x in n for x in full_catalog):
            return {'response':self.catalog(language),'route':'school_catalog'}
        subject=''
        for candidate in ('mathematics','math','science','language','history','humanities','geography','computing','computer science','health','life skills','arts','music','economics','civics','μαθηματικα','επιστημες','γλωσσα','ιστορια','γεωγραφια','πληροφορικη','υγεια','τεχνες','μουσικη','οικονομικα'):
            if norm(candidate) in n: subject=candidate; break
        if grade is not None and any(k in n for k in ('curriculum','topics','subjects','syllabus','knowledge map','υλη','θεματα','μαθηματα','προγραμμα','γνωσεις')):
            overview=self.grade_overview(grade,subject,language)
            if overview: return {'response':overview,'route':'school_grade_overview','grade':grade}
        math_answer=self._math(text,language)
        if math_answer: return math_answer
        school_markers=('what is','explain','teach me','define','how does','school','homework','grade','class','lesson','in detail','detailed','τι ειναι','εξηγησε','μαθε μου','ορισε','σχολειο','εργασια','ταξη','μαθημα','αναλυτικα','λεπτομερως')
        if any(m in n for m in school_markers) or grade is not None:
            return self._topic(text,language,grade=grade,depth=depth)
        return None
    def catalog(self,language='en')->str:
        subjects=9
        if language=='el':
            return (f'Πλήρης σχολική βάση για τάξεις 1-12: {self.topic_count:,} βασικές έννοιες και {self.grade_lesson_count:,} προσαρμοσμένα μαθήματα τάξης. '
                    'Καλύπτει Μαθηματικά, Γλώσσα και Λογοτεχνία, Φυσικές Επιστήμες, Ιστορία και Ανθρωπιστικές Επιστήμες, Γεωγραφία, Πληροφορική, Υγεία και Δεξιότητες Ζωής, Τέχνες και Μουσική, Οικονομικά και Αγωγή του Πολίτη. '
                    'Κάθε αναλυτικό μάθημα περιλαμβάνει στόχο, προαπαιτούμενα, βασική εξήγηση, στρατηγική μάθησης, λεξιλόγιο, παράδειγμα, συνηθισμένο λάθος, εξάσκηση, έλεγχο κατάκτησης, σχετικά θέματα και τοπικά τεκμήρια.')
        return (f'Complete grade 1-12 school foundation: {self.topic_count:,} core concepts and {self.grade_lesson_count:,} grade-adapted lessons. '
                'It covers mathematics, language and literature, science, history and humanities, geography, computing, health and life skills, arts and music, economics and civics. '
                'Each detailed lesson can include a goal, prerequisites, core explanation, learning strategy, vocabulary, guided example, misconception, practice, mastery check, related topics, and local evidence.')

    def instruction(self,language='en')->str:
        if language=='el': return 'Μίλα σαν φυσικός, υπομονετικός δάσκαλος. Προσαρμόζεις το βάθος στην τάξη και στο αίτημα, εξηγείς τη λογική πριν από την απομνημόνευση, δίνεις παραδείγματα, ελέγχεις παρανοήσεις και δεν παρουσιάζεις αβεβαιότητες ως γεγονότα.'
        return 'Speak like a natural, patient teacher. Adapt depth to the grade and request, explain reasoning before memorization, use examples, check misconceptions, and never present uncertainty as fact.'
