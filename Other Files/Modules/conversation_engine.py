"""Natural bilingual conversation, persistent follow-ups, and topic continuity."""
from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Optional, Sequence, Tuple

MODULE_VERSION = 6


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value).casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", re.sub(r"[^0-9a-zα-ω]+", " ", value)).strip()


def _choice(options: Sequence[str], seed: str) -> str:
    digest = hashlib.sha256(seed.encode("utf-8", errors="ignore")).digest()
    return options[digest[0] % len(options)]


def _recent_turns(history, maximum: int = 12):
    try:
        rows = list(history)[-maximum:]
    except Exception:
        return []
    return [(str(role), str(text)) for role, text in rows if str(text).strip()]


class ConversationEngine:
    """Tracks a coherent topic instead of treating every message as isolated."""

    def __init__(self) -> None:
        self.last_topic = ""
        self.last_assistant_excerpt = ""
        self.last_mode = "normal"

    def restore(self, history) -> None:
        rows = _recent_turns(history, 16)
        for role, text in reversed(rows):
            if role == "assistant" and not self.last_assistant_excerpt:
                self.last_assistant_excerpt = text[:1200]
            elif role == "user" and not self.last_topic:
                self.last_topic = text[:700]
            if self.last_topic and self.last_assistant_excerpt:
                break

    def social_reply(self, text: str, language: str, assistant_name: str, user_name: str = "") -> Optional[str]:
        n = _norm(text)
        en = {
            "greet": ("Hi! What are we working on?", "Hello! Continue naturally—I will keep the context.", "Hey! I’m ready."),
            "thanks": ("You’re welcome.", "Glad that helped.", "Any time."),
            "how": ("I’m ready and following the conversation. How are you doing?", "I’m working normally. What should we continue with?"),
            "name": (f"I’m {assistant_name}.",),
            "sorry": ("No problem. Tell me what felt wrong and I’ll approach it differently.", "That’s okay—we can correct it and continue."),
            "tired": ("That sounds tiring. Let’s reduce it to one small next step.", "Take it one step at a time. A short break may help too."),
            "happy": ("I’m glad to hear that.", "That’s good news!"),
            "sad": ("I’m sorry you’re going through that. We can talk about it or focus on one practical next step.",),
            "capabilities": ("I can hold a continuing English or Greek conversation, search current public web sources when enabled, learn public pages into local retrieval memory, explain school subjects, solve exact tasks, and use stronger local models when the phone can run them.",),
            "joke": ("Why did the computer take a break? It needed to clear its cache.", "Why was the math book worried? It had too many problems."),
            "night": ("Good night. I hope you get some proper rest.",),
            "bye": ("See you later.", "Take care."),
        }
        el = {
            "greet": ("Γεια! Με τι ασχολούμαστε;", "Γεια σου! Συνέχισε φυσικά—θα κρατήσω το πλαίσιο.", "Γεια! Είμαι έτοιμο."),
            "thanks": ("Παρακαλώ.", "Χαίρομαι που βοήθησε.", "Οποιαδήποτε στιγμή."),
            "how": ("Είμαι έτοιμο και ακολουθώ τη συζήτηση. Εσύ πώς είσαι;", "Λειτουργώ κανονικά. Με τι θέλεις να συνεχίσουμε;"),
            "name": (f"Είμαι το {assistant_name}.",),
            "sorry": ("Κανένα πρόβλημα. Πες μου τι δεν σου φάνηκε σωστό και θα το προσεγγίσω διαφορετικά.", "Εντάξει—μπορούμε να το διορθώσουμε και να συνεχίσουμε."),
            "tired": ("Ακούγεται κουραστικό. Ας το μειώσουμε σε ένα μικρό επόμενο βήμα.", "Πήγαινε ένα βήμα τη φορά. Ίσως βοηθήσει και ένα μικρό διάλειμμα."),
            "happy": ("Χαίρομαι που το ακούω.", "Αυτό είναι καλό νέο!"),
            "sad": ("Λυπάμαι που το περνάς αυτό. Μπορούμε να το συζητήσουμε ή να βρούμε ένα πρακτικό επόμενο βήμα.",),
            "capabilities": ("Μπορώ να κρατώ συνεχή συζήτηση στα Ελληνικά ή στα Αγγλικά, να αναζητώ τρέχουσες δημόσιες πηγές όταν είναι ενεργό το web, να μαθαίνω δημόσιες σελίδες στην τοπική μνήμη ανάκτησης, να εξηγώ σχολικά μαθήματα, να λύνω ακριβείς εργασίες και να χρησιμοποιώ ισχυρότερα τοπικά μοντέλα όταν το κινητό τα σηκώνει.",),
            "joke": ("Γιατί έκανε διάλειμμα ο υπολογιστής; Για να καθαρίσει την cache του.", "Γιατί ανησυχούσε το βιβλίο μαθηματικών; Είχε πάρα πολλά προβλήματα."),
            "night": ("Καληνύχτα. Ελπίζω να ξεκουραστείς καλά.",),
            "bye": ("Τα λέμε αργότερα.", "Να προσέχεις."),
        }
        table = el if language == "el" else en
        exact = lambda values: n in {_norm(v) for v in values}
        if exact({"hi", "hello", "hey", "hello there", "good morning", "good evening", "γεια", "γεια σου", "καλημερα", "καλησπερα"}):
            key = "greet"
        elif exact({"thanks", "thank you", "thx", "ευχαριστω", "σε ευχαριστω"}):
            key = "thanks"
        elif exact({"how are you", "are you okay", "πως εισαι", "τι κανεις"}):
            key = "how"
        elif exact({"what is your name", "whats your name", "who are you", "πως σε λενε", "ποιος εισαι"}):
            key = "name"
        elif exact({"sorry", "my mistake", "συγγνωμη", "λαθος μου"}):
            key = "sorry"
        elif exact({"i am tired", "im tired", "i feel tired", "ειμαι κουρασμενος", "ειμαι κουρασμενη"}):
            key = "tired"
        elif exact({"i am happy", "im happy", "ειμαι χαρουμενος", "ειμαι χαρουμενη"}):
            key = "happy"
        elif exact({"i am sad", "im sad", "ειμαι λυπημενος", "ειμαι λυπημενη"}):
            key = "sad"
        elif exact({"what can you do", "how can you help", "τι μπορεις να κανεις", "πως μπορεις να βοηθησεις"}):
            key = "capabilities"
        elif exact({"tell me a joke", "say a joke", "πες μου ενα αστειο", "πες ενα αστειο"}):
            key = "joke"
        elif exact({"good night", "night", "καληνυχτα"}):
            key = "night"
        elif exact({"bye", "goodbye", "see you", "αντιο", "τα λεμε"}):
            key = "bye"
        else:
            return None
        answer = _choice(table[key], n + assistant_name)
        if user_name and key == "greet" and len(user_name) < 30:
            answer = f"{user_name}, " + answer[0].lower() + answer[1:]
        return answer

    @staticmethod
    def _mode(text: str) -> str:
        n = _norm(text)
        modes = {
            "deeper": {"tell me more", "explain more", "more details", "go deeper", "continue", "keep going", "πες μου περισσοτερα", "εξηγησε περισσοτερο", "περισσοτερες λεπτομερειες", "σε βαθος", "συνεχισε"},
            "simple": {"make it simpler", "explain simply", "simpler", "easy words", "i dont understand", "i do not understand", "this makes no sense", "πιο απλα", "εξηγησε απλα", "με απλα λογια", "δεν καταλαβαινω", "δεν βγαζει νοημα", "μπερδευτηκα"},
            "example": {"give me an example", "give another example", "another example", "show an example", "show another example", "example", "give another one", "δωσε παραδειγμα", "δωσε αλλο παραδειγμα", "αλλο παραδειγμα", "δειξε αλλο παραδειγμα", "παραδειγμα", "δωσε αλλο"},
            "analogy": {"give me an analogy", "use an analogy", "analogy", "κανε μια αναλογια", "δωσε αναλογια"},
            "quiz": {"quiz me", "test me", "ask me a question", "κανε μου κουιζ", "εξετασε με", "κανε μου μια ερωτηση"},
            "why": {"why", "why is that", "why does that happen", "γιατι", "για ποιο λογο"},
            "how": {"how does it work", "how", "how exactly", "πως λειτουργει", "πως ακριβως", "πως"},
            "clarify": {"what do you mean", "which one", "what is that", "can you clarify", "τι εννοεις", "ποιο", "τι ειναι αυτο", "διευκρινισε"},
        }
        for key, values in modes.items():
            normalized = {_norm(value) for value in values}
            if n in normalized or any(n.startswith(value + " ") for value in normalized if len(value.split()) <= 4):
                return key
        # Short referential messages should inherit context even without an exact phrase.
        tokens = n.split()
        referential = {"it", "that", "this", "they", "them", "he", "she", "those", "these", "αυτο", "αυτη", "αυτος", "εκεινο", "αυτα", "τους", "το"}
        if len(tokens) <= 10 and any(token in referential for token in tokens):
            return "clarify"
        if len(tokens) <= 7 and (n.startswith("and ") or n.startswith("what about ") or n.startswith("και ") or n.startswith("τι γινεται με ")):
            return "deeper"
        return ""

    def contextualize(self, text: str, history, language: str, last_topic: str = "") -> Tuple[str, bool]:
        mode = self._mode(text)
        if not mode:
            # Remember a substantive new topic for the next short follow-up.
            if len(_norm(text).split()) >= 3:
                self.last_topic = str(text)[:900]
            return text, False

        rows = _recent_turns(history, 18)
        previous_user = ""
        previous_answer = ""
        current_norm = _norm(text)
        for role, value in reversed(rows):
            if role == "assistant" and not previous_answer:
                previous_answer = value[:1400]
            elif role == "user" and _norm(value) != current_norm:
                previous_user = value[:900]
                break

        topic = previous_user or last_topic or self.last_topic
        if not topic:
            return text, False
        self.last_topic = topic
        self.last_assistant_excerpt = previous_answer
        self.last_mode = mode

        if language == "el":
            instructions = {
                "deeper": "Συνέχισε με μεγαλύτερο βάθος και πρόσθεσε νέα ουσία, όχι επανάληψη.",
                "simple": "Ξαναεξήγησε το θέμα από την αρχή με πολύ απλά λόγια, μικρά βήματα και νέο συγκεκριμένο παράδειγμα.",
                "example": "Δώσε νέο, συγκεκριμένο και πλήρως λυμένο παράδειγμα που δεν επαναλαμβάνει το προηγούμενο.",
                "analogy": "Χρησιμοποίησε καθαρή αναλογία και εξήγησε πού παύει να είναι ακριβής.",
                "quiz": "Κάνε μόνο μία κατάλληλη ερώτηση, περίμενε την απάντηση του χρήστη και μετά δώσε ανατροφοδότηση.",
                "why": "Εξήγησε την αιτία, τον μηχανισμό και τη σύνδεση με το προηγούμενο θέμα.",
                "how": "Εξήγησε τη διαδικασία βήμα προς βήμα.",
                "clarify": "Διευκρίνισε ακριβώς σε τι αναφέρεται το προηγούμενο σημείο και εξήγησέ το φυσικά.",
            }
            context = f"Συνέχεια συζήτησης. Προηγούμενο θέμα: {topic}. {instructions[mode]} Τρέχον μήνυμα: {text}."
            if previous_answer:
                context += f" Προηγούμενη απάντηση για αναφορά: {previous_answer[:900]}"
            return context, True

        instructions = {
            "deeper": "Continue with greater depth and add new substance rather than repeating the same answer.",
            "simple": "Rebuild the explanation from the beginning using very simple words, small steps, and a new concrete example.",
            "example": "Give a new, concrete, fully worked example that does not repeat the previous one.",
            "analogy": "Use a clear analogy and explain where the analogy stops being accurate.",
            "quiz": "Ask exactly one suitable question, wait for the user's answer, and then give feedback.",
            "why": "Explain the cause, mechanism, and connection to the previous topic.",
            "how": "Explain the process step by step.",
            "clarify": "Clarify exactly what the previous reference means and explain it naturally.",
        }
        context = f"Continue the conversation. Previous topic: {topic}. {instructions[mode]} Current message: {text}."
        if previous_answer:
            context += f" Previous answer for reference: {previous_answer[:900]}"
        return context, True

    def instruction(self, text: str, language: str) -> str:
        n = _norm(text)
        if language == "el":
            base = (
                "Απάντησε σαν φυσικός, προσεκτικός συνομιλητής. Κράτησε τη συνέχεια της συζήτησης, "
                "λύσε αναφορές όπως ‘αυτό’ από τα προηγούμενα μηνύματα, απάντησε πρώτα στο πραγματικό αίτημα, "
                "χρησιμοποίησε ποικίλες προτάσεις και απόφυγε άκαμπτα πρότυπα, περιττές επικεφαλίδες και επανάληψη."
            )
            if any(value in n for value in ("αναλυτικα", "λεπτομερως", "σε βαθος", "ολα για")):
                base += " Δώσε ολοκληρωμένη αλλά οργανωμένη εξήγηση με μηχανισμό, παραδείγματα, συνδέσεις και έλεγχο κατανόησης."
            return base
        base = (
            "Answer like a natural, attentive conversational partner. Preserve conversation continuity, resolve references such as ‘that’ from prior turns, "
            "answer the actual request first, vary sentence structure, and avoid rigid templates, unnecessary headings, and repetition."
        )
        if any(value in n for value in ("in detail", "detailed", "deep", "everything about", "comprehensive")):
            base += " Give a comprehensive but organized explanation with mechanism, examples, connections, and a way to check understanding."
        return base

    def followup_prompt(self, question: str, answer: str, language: str, task_profile=None, context_used: bool = False) -> str:
        """Return one concise, topic-appropriate continuation prompt."""
        if not answer or answer.rstrip().endswith("?"):
            return ""
        normalized = _norm(question)
        if any(cue in normalized for cue in ("quiz me", "test me", "κανε μου κουιζ", "εξετασε με")):
            return ""
        profile = task_profile or {}
        task = str(profile.get("task", ""))
        if task in {"coding", "command", "calculation"} or "```" in answer:
            return ""
        if len(answer.split()) < 35 and not context_used and not profile.get("school_query"):
            return ""
        if language == "el":
            options = (
                "Θέλεις να το συνεχίσουμε πιο απλά, με παράδειγμα ή με ένα σύντομο κουίζ;",
                "Να εμβαθύνω σε κάποιο συγκεκριμένο σημείο ή να δώσω ένα πρακτικό παράδειγμα;",
                "Ποιο μέρος θέλεις να αναλύσουμε περισσότερο;",
            )
        else:
            options = (
                "Would you like to continue with a simpler explanation, an example, or a short quiz?",
                "Should I go deeper into one part or show a practical example?",
                "Which part would you like to explore further?",
            )
        return _choice(options, _norm(question) + str(len(answer)))
