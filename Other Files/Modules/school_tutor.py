#!/usr/bin/env python3
"""Shared bilingual grade 1-12 school tutor for Pocket AI.

The module uses only Python's standard library. It provides deterministic math
solvers and a compact bilingual curriculum knowledge pack. It runs before any
optional GGUF model, so every hardware/model profile receives the same basic
school capabilities.
"""
from __future__ import annotations
import ast, difflib, gzip, json, math, re, statistics, unicodedata
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SPACE_RE=re.compile(r"\s+")

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
        self.path=Path(knowledge_path); self.pack={'topics':[],'grades':{}}
        try:
            with gzip.open(self.path,'rt',encoding='utf-8') as f: self.pack=json.load(f)
        except Exception: pass
        self.alias=[]
        for item in self.pack.get('topics',[]):
            for a in item.get('aliases',[]): self.alias.append((norm(str(a)),item))
    @staticmethod
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
        data=self.pack.get('grades',{}).get(str(grade),{})
        if not data: return ''
        aliases={'mathematics':'math','maths':'math','math':'math','μαθηματικα':'math','science':'science','επιστημη':'science','φυσικες επιστημες':'science','language':'language','english':'language','greek':'language','γλωσσα':'language','αγγλικα':'language','ελληνικα':'language','history':'humanities','geography':'humanities','humanities':'humanities','ιστορια':'humanities','γεωγραφια':'humanities','computing':'computing','computer':'computing','πληροφορικη':'computing'}
        subject_key = re.sub(r'\b(?:topics?|subjects?|curriculum|θεματα|μαθηματα|υλη)\b', ' ', norm(subject)).strip() if subject else ''
        key=aliases.get(subject_key,subject_key) if subject_key else ''
        keys=[key] if key in data else list(data)
        if language=='el':
            title=f'Βασικά θέματα για την τάξη {grade}'
            lines=[title]
            labels={'math':'Μαθηματικά','language':'Γλώσσα','science':'Επιστήμες','humanities':'Ιστορία και Γεωγραφία','computing':'Πληροφορική'}
        else:
            title=f'Core topics for grade {grade}'
            lines=[title]
            labels={'math':'Mathematics','language':'Language','science':'Science','humanities':'History and Geography','computing':'Computing'}
        for k in keys:
            values = data[k]
            if language == 'el': values = [GRADE_TRANSLATIONS.get(value, value) for value in values]
            lines.append(f"- {labels.get(k,k.title())}: "+'; '.join(values))
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
    def _topic(self,text:str,language:str)->Optional[dict]:
        n=norm(text); query_terms=set(n.split())
        best=None
        for alias,item in self.alias:
            if not alias: continue
            alias_terms=set(alias.split()); overlap=len(query_terms & alias_terms)
            coverage=overlap/max(1,len(alias_terms)); seq=difflib.SequenceMatcher(None,n,alias).ratio()
            contains=1.0 if alias in n else 0.0
            score=0.5*coverage+0.2*seq+0.3*contains
            if best is None or score>best[0]: best=(score,item,alias)
        if best and best[0]>=0.61:
            item=best[1]
            return {'response':item.get('el' if language=='el' else 'en',''),'route':'school_knowledge','subject':item.get('subject'),'grades':item.get('grades'),'topic':item.get('id'),'match':best[0]}
        return None
    def answer(self,text:str,language:str='en')->Optional[dict]:
        n=norm(text)
        if n in {'school help','help with school','school tutor','σχολικη βοηθεια','βοηθεια για σχολειο','σχολικος βοηθος'}:
            return {'response': self.catalog(language), 'route':'school_catalog'}
        # Grade overview requests
        m=re.search(r'(?:grade|class|year|ταξη)\s*(1[0-2]|[1-9])(?:\s+([a-zα-ω ]+))?',n)
        if m and any(k in n for k in ('grade','class','year','ταξη','curriculum','topics','subjects','υλη','θεματα')):
            overview=self.grade_overview(int(m.group(1)),(m.group(2) or '').strip(),language)
            if overview: return {'response':overview,'route':'school_grade_overview','grade':int(m.group(1))}
        math_answer=self._math(text,language)
        if math_answer: return math_answer
        school_markers=('what is','explain','teach me','define','how does','school','homework','grade','τι ειναι','εξηγησε','μαθε μου','ορισε','σχολειο','εργασια','ταξη')
        if any(m in n for m in school_markers): return self._topic(text,language)
        return None
    def catalog(self,language='en')->str:
        if language=='el':
            return 'Σχολική βάση: τάξεις 1-12· Μαθηματικά, Επιστήμες, Ελληνικά/Αγγλικά, Ιστορία, Γεωγραφία, Αγωγή Πολίτη, Οικονομικά, Πληροφορική και δεξιότητες μελέτης.'
        return 'School foundation: grades 1-12; mathematics, science, English/Greek language, history, geography, civics, economics, computing, and study skills.'
    def instruction(self,language='en')->str:
        if language=='el': return 'Για σχολικές ερωτήσεις, εξήγησε στο κατάλληλο επίπεδο τάξης, δείξε βήματα στα μαθηματικά και μην παρουσιάζεις αβεβαιότητες ως γεγονότα.'
        return 'For school questions, explain at an appropriate grade level, show mathematical steps, and never present uncertainty as fact.'
