"""Natural bilingual conversation, clarification, and follow-up understanding."""
from __future__ import annotations
import hashlib,re,unicodedata
from typing import Optional,Tuple

MODULE_VERSION=4

def _norm(s:str)->str:
    s=unicodedata.normalize('NFKD',str(s).casefold())
    s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'\s+',' ',re.sub(r'[^0-9a-zα-ω]+',' ',s)).strip()

def _choice(options,seed):
    digest=hashlib.sha256(seed.encode('utf-8',errors='ignore')).digest()
    return options[digest[0]%len(options)]

class ConversationEngine:
    def __init__(self)->None:
        self.last_topic=''
        self.last_assistant_excerpt=''
        self.last_mode='normal'

    def social_reply(self,text:str,language:str,assistant_name:str,user_name:str='')->Optional[str]:
        n=_norm(text)
        en={
          'greet':("Hi! What are we working on?","Hello! Ask naturally—I'll follow the context.","Hey! I'm ready."),
          'thanks':("You're welcome.","Glad that helped.","Any time."),
          'how':("I'm working normally and ready to help. How are you doing?","I'm ready. What would you like to understand or build?"),
          'name':(f"I'm {assistant_name}.",),
          'sorry':("No problem. Tell me what felt wrong and I'll approach it differently.","That's okay—we can correct it and continue."),
          'confused':("That's fine. Tell me which part stopped making sense, and I'll explain it with simpler words and a different example.","Let's slow it down. I can rebuild the explanation from the beginning without assuming the difficult part."),
          'tired':("That sounds tiring. Let's reduce it to one small next step.","Take it one step at a time. A short break may help too."),
          'happy':("I'm glad to hear that.","That's good news!"),
          'sad':("I'm sorry you're going through that. We can talk about it or focus on one practical next step.",),
          'capabilities':("I can explain school subjects, reason from the local knowledge base, solve many exact math tasks, help with code, and continue earlier context in English or Greek.",),
          'joke':("Why did the computer take a break? It needed to clear its cache.","Why was the math book worried? It had too many problems."),
          'night':("Good night. I hope you get some proper rest.",),
          'bye':("See you later.","Take care."),
        }
        el={
          'greet':("Γεια! Με τι ασχολούμαστε;","Γεια σου! Ρώτησέ με φυσικά—θα ακολουθήσω το πλαίσιο.","Γεια! Είμαι έτοιμο."),
          'thanks':("Παρακαλώ.","Χαίρομαι που βοήθησε.","Οποιαδήποτε στιγμή."),
          'how':("Λειτουργώ κανονικά και είμαι έτοιμο να βοηθήσω. Εσύ πώς είσαι;","Είμαι έτοιμο. Τι θέλεις να καταλάβεις ή να δημιουργήσεις;"),
          'name':(f"Είμαι το {assistant_name}.",),
          'sorry':("Κανένα πρόβλημα. Πες μου τι δεν σου φάνηκε σωστό και θα το προσεγγίσω διαφορετικά.","Εντάξει—μπορούμε να το διορθώσουμε και να συνεχίσουμε."),
          'confused':("Εντάξει. Πες μου σε ποιο σημείο χάθηκε το νόημα και θα το εξηγήσω με πιο απλά λόγια και διαφορετικό παράδειγμα.","Ας το πάμε πιο αργά. Μπορώ να ξαναχτίσω την εξήγηση από την αρχή χωρίς να θεωρώ δεδομένο το δύσκολο μέρος."),
          'tired':("Ακούγεται κουραστικό. Ας το μειώσουμε σε ένα μικρό επόμενο βήμα.","Πήγαινε ένα βήμα τη φορά. Ίσως βοηθήσει και ένα μικρό διάλειμμα."),
          'happy':("Χαίρομαι που το ακούω.","Αυτό είναι καλό νέο!"),
          'sad':("Λυπάμαι που το περνάς αυτό. Μπορούμε να το συζητήσουμε ή να βρούμε ένα πρακτικό επόμενο βήμα.",),
          'capabilities':("Μπορώ να εξηγώ σχολικά μαθήματα, να συλλογίζομαι πάνω στην τοπική βάση γνώσης, να λύνω πολλές ακριβείς μαθηματικές εργασίες, να βοηθώ με κώδικα και να συνεχίζω το προηγούμενο πλαίσιο στα Ελληνικά ή στα Αγγλικά.",),
          'joke':("Γιατί έκανε διάλειμμα ο υπολογιστής; Για να καθαρίσει την cache του.","Γιατί ανησυχούσε το βιβλίο μαθηματικών; Είχε πάρα πολλά προβλήματα."),
          'night':("Καληνύχτα. Ελπίζω να ξεκουραστείς καλά.",),
          'bye':("Τα λέμε αργότερα.","Να προσέχεις."),
        }
        table=el if language=='el' else en
        exact=lambda values:n in {_norm(v) for v in values}
        if exact({'hi','hello','hey','hello there','good morning','good evening','γεια','γεια σου','καλημερα','καλησπερα'}): key='greet'
        elif exact({'thanks','thank you','thx','ευχαριστω','σε ευχαριστω'}): key='thanks'
        elif exact({'how are you','are you okay','πως εισαι','τι κανεις'}): key='how'
        elif exact({'what is your name','whats your name','who are you','πως σε λενε','ποιος εισαι'}): key='name'
        elif exact({'sorry','my mistake','συγγνωμη','λαθος μου'}): key='sorry'
        elif any(cue in n for cue in ('i dont understand','i do not understand','i am confused','this makes no sense','δεν καταλαβαινω','μπερδευτηκα','δεν βγαζει νοημα')): key='confused'
        elif exact({'i am tired','im tired','i feel tired','ειμαι κουρασμενος','ειμαι κουρασμενη'}): key='tired'
        elif exact({'i am happy','im happy','ειμαι χαρουμενος','ειμαι χαρουμενη'}): key='happy'
        elif exact({'i am sad','im sad','ειμαι λυπημενος','ειμαι λυπημενη'}): key='sad'
        elif exact({'what can you do','how can you help','τι μπορεις να κανεις','πως μπορεις να βοηθησεις'}): key='capabilities'
        elif exact({'tell me a joke','say a joke','πες μου ενα αστειο','πες ενα αστειο'}): key='joke'
        elif exact({'good night','night','καληνυχτα'}): key='night'
        elif exact({'bye','goodbye','see you','αντιο','τα λεμε'}): key='bye'
        else:return None
        answer=_choice(table[key],n+assistant_name)
        if user_name and key=='greet' and len(user_name)<30: answer=f"{user_name}, "+answer[0].lower()+answer[1:]
        return answer

    def contextualize(self,text:str,history,language:str,last_topic:str='')->Tuple[str,bool]:
        n=_norm(text)
        modes={
          'deeper':{'tell me more','explain more','more details','go deeper','continue','πες μου περισσοτερα','εξηγησε περισσοτερο','περισσοτερες λεπτομερειες','σε βαθος','συνεχισε'},
          'simple':{'make it simpler','explain simply','simpler','easy words','i dont understand','πιο απλα','εξηγησε απλα','με απλα λογια','δεν καταλαβαινω'},
          'example':{'give me an example','another example','show an example','example','δωσε παραδειγμα','αλλο παραδειγμα','παραδειγμα'},
          'analogy':{'give me an analogy','use an analogy','analogy','κανε μια αναλογια','δωσε αναλογια'},
          'quiz':{'quiz me','test me','ask me a question','κανε μου κουιζ','εξετασε με','κανε μου μια ερωτηση'},
          'why':{'why','why is that','γιατι','για ποιο λογο'},
          'how':{'how does it work','how','πως λειτουργει','πως'},
        }
        mode=''
        for key,values in modes.items():
            normalized={_norm(v) for v in values}
            if n in normalized or any(n.startswith(v+' ') for v in normalized if len(v.split())<=3): mode=key; break
        if not mode:return text,False
        previous=''
        assistant_excerpt=''
        try:
            rows=list(history)
            for role,value in reversed(rows):
                if role=='assistant' and not assistant_excerpt: assistant_excerpt=str(value)[:900]
                if role=='user' and _norm(value)!=n:
                    previous=str(value); break
        except Exception:pass
        topic=previous or last_topic or self.last_topic
        if not topic:return text,False
        self.last_topic=topic; self.last_assistant_excerpt=assistant_excerpt; self.last_mode=mode
        if language=='el':
            instruction={'deeper':'Συνέχισε με μεγαλύτερο βάθος, μη επαναλάβεις απλώς την ίδια απάντηση.','simple':'Ξαναεξήγησε το θέμα με πολύ απλά λόγια και νέο συγκεκριμένο παράδειγμα.','example':'Δώσε ένα νέο, συγκεκριμένο και πλήρως λυμένο παράδειγμα.','analogy':'Χρησιμοποίησε μια καθαρή αναλογία και εξήγησε πού σταματά να ισχύει.','quiz':'Κάνε μία ερώτηση κάθε φορά, περίμενε απάντηση και μετά δώσε ανατροφοδότηση.','why':'Εξήγησε την αιτία και τον μηχανισμό.','how':'Εξήγησε τη διαδικασία βήμα προς βήμα.'}[mode]
            return f"Συνέχεια του θέματος «{topic}». {instruction} Τρέχον αίτημα: {text}",True
        instruction={'deeper':'Continue at greater depth; do not merely repeat the same answer.','simple':'Re-explain it in very simple language with a new concrete example.','example':'Give a new, concrete, fully worked example.','analogy':'Use a clear analogy and explain where the analogy stops being accurate.','quiz':'Ask one question at a time, wait for an answer, then give feedback.','why':'Explain the cause and mechanism.','how':'Explain the process step by step.'}[mode]
        return f"Continue the topic '{topic}'. {instruction} Current request: {text}",True

    def instruction(self,text:str,language:str)->str:
        n=_norm(text)
        if language=='el':
            base='Απάντησε σαν φυσικός, προσεκτικός συνομιλητής. Κατανόησε την πρόθεση, κράτησε το προηγούμενο πλαίσιο, χρησιμοποίησε ποικίλες προτάσεις και απόφυγε άκαμπτα πρότυπα, περιττές επικεφαλίδες και επανάληψη της ερώτησης.'
            if any(x in n for x in ('αναλυτικα','λεπτομερως','σε βαθος','ολα για')): base+=' Δώσε ολοκληρωμένη αλλά οργανωμένη εξήγηση, με μηχανισμό, παραδείγματα, συνδέσεις και έλεγχο κατανόησης.'
            return base
        base='Answer like a natural, attentive conversational partner. Understand the intent, preserve prior context, vary sentence structure, and avoid rigid templates, unnecessary headings, and repeating the question.'
        if any(x in n for x in ('in detail','detailed','deep','everything about','comprehensive')): base+=' Give a comprehensive but organized explanation with mechanism, examples, connections, and a way to check understanding.'
        return base
