<div align="center">
  <img src="https://raw.githubusercontent.com/dedsec1121fk/dedsec1121fk.github.io/47ad8e5cbaaee04af552ae6b90edc49cd75b324b/Assets/Images/Logos/Black%20Purple%20Butterfly%20Logo.jpeg" alt="DedSec Project Logo" width="150"/>
  <h1>Pocket AI</h1>
  <p><strong>Private bilingual local AI for Android + Termux</strong></p>
  <p>
    <a href="https://ded-sec.space/"><strong>DedSec Project Website</strong></a>
    ·
    <a href="https://github.com/sponsors/dedsec1121fk"><strong>Sponsor the Project</strong></a>
  </p>
  <p>
    <img src="https://img.shields.io/badge/Platform-Android%20%2B%20Termux-brightgreen.svg" alt="Android + Termux">
    <img src="https://img.shields.io/badge/Interface-English%20%7C%20Greek-lightgrey.svg" alt="English and Greek">
    <img src="https://img.shields.io/badge/Root-Not%20Required-blue.svg" alt="No root required">
    <img src="https://img.shields.io/badge/Models-Bundled-purple.svg" alt="Models bundled">
    <img src="https://img.shields.io/badge/Cloud-Not%20Required-black.svg" alt="Cloud not required">
  </p>
</div>

---

<a id="english"></a>

# Pocket AI — English

> **Για την πλήρη Ελληνική έκδοση, μεταβείτε [εδώ](#ελληνικά).**

Pocket AI is a bilingual **English and Greek local AI assistant** designed for Android phones running Termux without root. It automatically scans the phone, measures usable resources, and selects the safest combination of neural classifier, local language model, runtime profile, and hybrid mode.

The package is built for old and low-cost phones as well as stronger devices. It can fall back to its lightweight internal engine when a GGUF model would be unsafe, while phones with more available RAM can use sequential hybrid inference for better answer quality.

Pocket AI does not claim to be a human. The optional human-conversation feature gives it a custom name and a more natural speaking style while it continues to identify itself as an AI assistant.

## Simple Use

Pocket AI opens directly in chat. There is no launcher to learn before asking a question.

```text
You: What is an apple?
Pocket AI: An apple is an edible fruit produced by an apple tree...
```

Type any normal English or Greek question and Pocket AI answers it. Type `help` or `βοήθεια` at any time to open a simple numbered menu.

```text
1. Return to chat
2. Scan phone and automatically choose the best model
3. Change the AI name and speaking style
4. Teach the AI a question and answer
5. Learn from a file or folder
6. Safely research the web and learn
7. Show active model and status
8. Show advanced commands
9. Exit
```

The phone scan also runs automatically on normal startup, so most users only need to launch the script and start talking.

### Automatic Phone Scan and Model Selection

The scanner checks:

- phone manufacturer and model
- processor and SoC identifiers
- ARM, ARM64, x86, or x86-64 architecture
- 32-bit or 64-bit Termux userspace
- CPU cores and frequency clusters
- short local CPU benchmark
- total and currently available RAM
- application and shared-storage capacity
- free storage space
- phone and battery temperature when exposed by Android
- battery status and power pressure
- bundled model availability, size, GGUF header, and checksum

Unknown or renamed processors are not rejected. Pocket AI uses measured architecture, cores, frequency, benchmark performance, RAM, and storage as a fallback.

### Direct Local Chat

If no scan exists, Pocket AI scans automatically. It then loads the recommended pre-trained classifier and configures the local GGUF runtime. Only one transformer model is loaded at a time. The normal screen waits at `You:` or `Εσύ:` for a question.

### Name & Humanize AI

This menu lets you set:

- the AI's name
- your optional name
- a conversation style
- whether natural human-like wording is enabled

Available styles:

| Style | Behavior |
| :--- | :--- |
| `friendly` | Warm, natural, and clear |
| `calm_expert` | Careful, professional explanations |
| `casual` | Relaxed and concise conversation |
| `mentor` | Patient step-by-step teaching |
| `direct` | Answer-first, minimal wording |

The settings are stored locally in:

```text
Other Files/Saved Data/persona.json
```

## Package Structure

```text
Pocket AI.py
README.md
Models/
Other Files/
```

### `Pocket AI.py`

The main application. It includes the terminal menu, phone scanner, neural classifier, local retrieval database, bilingual tools, web-learning controls, GGUF runner integration, and hybrid orchestration.

### `Models/`

Contains every bundled AI model and controller. Model weights are included in the ZIP and are not downloaded when Pocket AI starts.

### `Other Files/`

Contains runtime modules, documentation, licenses, checksums, the llama.cpp build helper, and all generated save data.

## Bundled Model Stack

Pocket AI contains multiple model layers that cooperate rather than pretending every small controller is a full transformer.

### GGUF Language Models

| Model | Purpose | Typical target |
| :--- | :--- | :--- |
| SmolLM2-135M Q2_K | Lowest-memory transformer responses | 2 GB-class phones and weak processors |
| SmolLM2-135M Q4_1 | Better quantization quality | 3 GB+ phones with enough available RAM |

### Pre-trained Bilingual Neural Classifiers

- Micro
- Lite
- Balanced
- Standard
- Max

The hardware scanner selects the classifier from RAM, available memory, CPU performance, and storage. These classifiers are pre-trained so old phones do not need to perform heavy first-run training.

### Bilingual MicroLM Models

- MicroLM Lite
- MicroLM Quality

These compact n-gram models provide lightweight local generation and fallback behavior.

### Task Specialists

- Coding and Termux specialist
- Mathematics specialist
- Public-research specialist

### Hybrid and Control Models

- Hybrid Router
- Query Planner
- Response Verifier
- Resource Guard
- Adaptive Controller
- Consensus Controller
- Persona Controller
- Context Optimizer
- Confidence Calibrator

The controllers are compact routing and scoring components, not large transformer models.

## Hybrid Modes

Use:

```text
/hybrid auto
/hybrid speed
/hybrid smart
/hybrid quality
/hybrid adaptive
/hybrid expert
/hybrid consensus
/hybrid cascade
/hybrid off
```

| Mode | How it works |
| :--- | :--- |
| `off` | Uses retrieval, tools, specialists, and the internal neural engine only |
| `speed` | Uses the Fast GGUF model in one pass |
| `smart` | Selects Fast or Quality from the question and live resources |
| `quality` | Prefers the Quality GGUF model |
| `adaptive` | Creates a Fast draft and skips the second pass when the draft is already strong |
| `expert` | Adds specialist guidance and optimized local context to the Quality model |
| `consensus` | Generates independent Fast and Quality answers sequentially, compares them, and selects the stronger result |
| `cascade` | Generates a Fast draft, unloads it, then verifies and rewrites it with Quality |
| `auto` | Selects a safe mode from CPU, RAM, temperature, model availability, and question complexity |

Fast and Quality models are executed sequentially in multi-pass modes. They are not kept in memory at the same time.

## Runtime Modules

The following standard-library modules are included under `Other Files/Modules/`:

- `persona_engine.py` — persistent AI identity and natural bilingual speaking styles
- `context_optimizer.py` — ranks local documents, memories, and recent conversation under a prompt budget
- `consensus_engine.py` — compares independent Fast and Quality answers
- `confidence_engine.py` — produces calibrated high, medium, or low answer confidence
- `resource_advisor.py` — explains why a hardware/model combination was selected

Pocket AI contains conservative fallbacks if one of these optional module files becomes damaged.

## English and Greek Only

Pocket AI accepts and produces English and Greek. Other scripts are rejected before they can enter training data, memories, document indexing, or local generation.

Use:

```text
/language auto
/language en
/language el
```

## Local Knowledge and Learning

### Teach a direct answer

```text
/teach What is Pocket AI? | Pocket AI is a bilingual local AI assistant for Termux.
```

### Correct the previous answer

```text
/correct The corrected answer goes here.
```

### Index a file or folder

```text
/ingest ~/storage/downloads/MyNotes
```

### Summarize a text file

```text
/summarize ~/storage/downloads/article.txt
```

### Save a persistent memory

```text
/remember project = DedSec Project
```

All learned data remains under `Other Files/Saved Data/` unless you explicitly use public-web learning.

## Public Web Learning and Search Operators

Pocket AI can perform explicit public research through `/dork` or `/web-learn`. This feature requires internet access and is not used automatically.

Supported public search operators include:

```text
site:
filetype:
intitle:
inurl:
before:
after:
"exact phrase"
-minusword
```

Example:

```text
/dork site:python.org sqlite tutorial
```

The web-learning system blocks requests aimed at exposed passwords, private keys, credentials, admin panels, databases, backups, cameras, routers, and private systems. Use it only for lawful public research.

## Installation in Termux

### Requirements

| Component | Requirement |
| :--- | :--- |
| Android | A device capable of running a current Termux build |
| Root | Not required |
| Python | Installed by the command below |
| Storage | Approximately 500 MB recommended for extraction, models, build files, and saves |
| RAM | Internal engine can run on very low memory; GGUF model use depends on live available RAM |
| Internet | Needed for Termux packages and building llama.cpp; model weights are already bundled |

Install:

```bash
termux-setup-storage
pkg update -y
pkg install python unzip -y

cd ~
rm -rf Pocket_AI
mkdir Pocket_AI
unzip -o ~/storage/downloads/Pocket_AI.zip -d ~/Pocket_AI

cd ~/Pocket_AI
chmod +x "Other Files/install_models.sh"
bash "Other Files/install_models.sh"

python "Pocket AI.py"
```

The installer builds the compatible `llama.cpp` executable. It does not download the bundled model weights.

## Useful Commands

```text
/help
/persona
/name NAME
/style friendly
/human on
/models
/system
/stats
/why
/teach QUESTION | ANSWER
/correct ANSWER
/ingest PATH
/summarize PATH
/remember KEY = VALUE
/memories
/forget KEY
/hybrid auto
/llm-status
/benchmark
/backup
/quit
```

Greek aliases are available for the most important commands, including `/βοήθεια`, `/όνομα`, `/προσωπικότητα`, `/στυλ`, `/ανθρώπινο`, `/υβριδικό`, `/μοντέλα`, `/γλώσσα`, and `/έξοδος`.

## Save Locations

```text
Other Files/Saved Data/device_profile.json
Other Files/Saved Data/persona.json
Other Files/Saved Data/knowledge.sqlite3
Other Files/Saved Data/dataset.json
Other Files/Saved Data/neural_model.pkl.gz
Other Files/Saved Data/model_metadata.json
Other Files/Saved Data/language_model.pkl.gz
Other Files/Saved Data/backups/
```

## Limitations

- Pocket AI is not comparable to a cloud-scale modern LLM.
- The bundled transformer models are intentionally small for older phones.
- Small models can produce incorrect or incomplete answers.
- Important medical, legal, financial, security, or current factual claims should be independently verified.
- Greek quality from the bundled English-focused GGUF model may be weaker than the bilingual internal retrieval and classifier layers.
- Phone vendors may hide temperature, battery, or SoC information; Pocket AI uses measured fallbacks when necessary.
- “Human-like” means natural conversational wording. It does not mean the program is human, conscious, or emotionally aware.

## Privacy

Core chat, retrieval, memories, documents, and models run locally. Pocket AI does not require a cloud API. Public web access occurs only when you explicitly run `/dork` or `/web-learn`.

Do not store secrets that should not exist in unencrypted local application data.

## Credits

- Creator and project: **dedsec1121fk / DedSec Project**
- Website: [ded-sec.space](https://ded-sec.space/)
- Sponsor: [GitHub Sponsors](https://github.com/sponsors/dedsec1121fk)
- Local runtime: `llama.cpp`
- Bundled model license information is available under `Other Files/Licenses/`.

## Disclaimer

Pocket AI is provided for educational, personal, and lawful local-assistant use. It is supplied **as is**, without guarantees of accuracy, compatibility, availability, or fitness for a particular purpose. The user is responsible for reviewing generated commands and answers before acting on them.

---

<a id="ελληνικά"></a>

# Pocket AI — Ελληνικά

> **To return to the full English version, continue [here](#english).**

Το Pocket AI είναι ένας δίγλωσσος **τοπικός βοηθός AI στα Αγγλικά και στα Ελληνικά**, σχεδιασμένος για Android κινητά που χρησιμοποιούν Termux χωρίς root. Σαρώνει αυτόματα το κινητό, μετρά τους διαθέσιμους πόρους και επιλέγει τον ασφαλέστερο συνδυασμό νευρωνικού classifier, τοπικού γλωσσικού μοντέλου, runtime profile και υβριδικής λειτουργίας.

Το πακέτο είναι σχεδιασμένο τόσο για παλιά και οικονομικά κινητά όσο και για ισχυρότερες συσκευές. Όταν ένα GGUF μοντέλο δεν είναι ασφαλές για τη διαθέσιμη RAM, χρησιμοποιεί την ελαφριά εσωτερική μηχανή. Σε κινητά με περισσότερους πόρους μπορεί να χρησιμοποιήσει διαδοχική υβριδική επεξεργασία για καλύτερη ποιότητα απαντήσεων.

Το Pocket AI δεν προσποιείται ότι είναι άνθρωπος. Η προαιρετική φυσική συνομιλία επιτρέπει να του δώσετε όνομα και πιο ανθρώπινο τρόπο έκφρασης, ενώ συνεχίζει να αναγνωρίζει ότι είναι βοηθός τεχνητής νοημοσύνης.

## Απλή Χρήση

Το Pocket AI ανοίγει απευθείας στη συνομιλία. Δεν χρειάζεται να μάθετε αρχικό μενού πριν κάνετε μία ερώτηση.

```text
Εσύ: Τι είναι ένα μήλο;
Pocket AI: Ένα μήλο είναι ένας βρώσιμος καρπός της μηλιάς...
```

Γράψτε οποιαδήποτε κανονική ερώτηση στα Ελληνικά ή στα Αγγλικά και το Pocket AI θα απαντήσει. Γράψτε `help` ή `βοήθεια` οποιαδήποτε στιγμή για να ανοίξει ένα απλό αριθμημένο μενού.

```text
1. Επιστροφή στη συνομιλία
2. Σάρωση κινητού και αυτόματη επιλογή καλύτερου μοντέλου
3. Αλλαγή ονόματος και τρόπου ομιλίας του AI
4. Δίδαξε στο AI μία ερώτηση και απάντηση
5. Μάθηση από αρχείο ή φάκελο
6. Ασφαλής έρευνα στο διαδίκτυο και μάθηση
7. Προβολή ενεργού μοντέλου και κατάστασης
8. Προβολή προχωρημένων εντολών
9. Έξοδος
```

Η σάρωση του κινητού εκτελείται αυτόματα στην κανονική εκκίνηση, επομένως οι περισσότεροι χρήστες χρειάζεται μόνο να ανοίξουν το script και να αρχίσουν να μιλούν.

### Αυτόματη Σάρωση Κινητού και Επιλογή Μοντέλου

Η σάρωση ελέγχει:

- κατασκευαστή και μοντέλο κινητού
- ονομασία επεξεργαστή και SoC
- ARM, ARM64, x86 ή x86-64 αρχιτεκτονική
- 32-bit ή 64-bit Termux userspace
- πυρήνες και συχνότητες CPU
- σύντομο τοπικό CPU benchmark
- συνολική και διαθέσιμη RAM
- συνολικό και ελεύθερο χώρο αποθήκευσης
- θερμοκρασία κινητού και μπαταρίας όταν το Android την παρέχει
- κατάσταση μπαταρίας και πίεση πόρων
- διαθεσιμότητα, μέγεθος, GGUF header και checksum των μοντέλων

Άγνωστοι ή μετονομασμένοι επεξεργαστές δεν απορρίπτονται. Το Pocket AI χρησιμοποιεί ως fallback την αρχιτεκτονική, τους πυρήνες, τις συχνότητες, το benchmark, τη RAM και την αποθήκευση.

### Άμεση Τοπική Συνομιλία

Αν δεν υπάρχει αποθηκευμένη σάρωση, πραγματοποιείται αυτόματα. Στη συνέχεια φορτώνεται ο προτεινόμενος pre-trained classifier και ρυθμίζεται το GGUF runtime. Μόνο ένα transformer μοντέλο φορτώνεται κάθε φορά. Η κανονική οθόνη περιμένει στο `You:` ή `Εσύ:` για την ερώτησή σας.

### Όνομα και Φυσική Συνομιλία

Η επιλογή επιτρέπει να ορίσετε:

- το όνομα του AI
- το δικό σας προαιρετικό όνομα
- το στυλ συζήτησης
- αν θα χρησιμοποιείται φυσική ανθρώπινη διατύπωση

Διαθέσιμα στυλ:

| Στυλ | Συμπεριφορά |
| :--- | :--- |
| `friendly` | Φιλικό, φυσικό και καθαρό |
| `calm_expert` | Ήρεμες και προσεκτικές εξηγήσεις ειδικού |
| `casual` | Χαλαρή και σύντομη συνομιλία |
| `mentor` | Υπομονετική διδασκαλία βήμα προς βήμα |
| `direct` | Άμεση απάντηση με ελάχιστη περιττή διατύπωση |

Οι ρυθμίσεις αποθηκεύονται τοπικά στο:

```text
Other Files/Saved Data/persona.json
```

## Δομή Πακέτου

```text
Pocket AI.py
README.md
Models/
Other Files/
```

### `Pocket AI.py`

Το κύριο πρόγραμμα με το terminal menu, τη σάρωση κινητού, τον νευρωνικό classifier, την τοπική βάση ανάκτησης, τα δίγλωσσα εργαλεία, το ελεγχόμενο web learning, το GGUF runtime και την υβριδική δρομολόγηση.

### `Models/`

Περιέχει όλα τα ενσωματωμένα AI μοντέλα και controllers. Τα model weights βρίσκονται ήδη μέσα στο ZIP και δεν κατεβαίνουν κατά την εκκίνηση.

### `Other Files/`

Περιέχει runtime modules, τεκμηρίωση, άδειες, checksums, το helper για τη δημιουργία του llama.cpp και όλα τα save data.

## Ενσωματωμένα Μοντέλα

### GGUF Γλωσσικά Μοντέλα

| Μοντέλο | Χρήση | Συνήθης στόχος |
| :--- | :--- | :--- |
| SmolLM2-135M Q2_K | Χαμηλότερη RAM και γρήγορες απαντήσεις | Κινητά περίπου 2 GB και αδύναμοι επεξεργαστές |
| SmolLM2-135M Q4_1 | Καλύτερη ποιότητα quantization | Κινητά 3 GB+ με αρκετή διαθέσιμη RAM |

### Pre-trained Δίγλωσσοι Classifiers

- Micro
- Lite
- Balanced
- Standard
- Max

Ο scanner επιλέγει classifier με βάση RAM, διαθέσιμη μνήμη, ταχύτητα επεξεργαστή και αποθήκευση. Είναι ήδη εκπαιδευμένοι ώστε τα παλιά κινητά να μη χρειάζονται βαριά εκπαίδευση στην πρώτη εκκίνηση.

### Δίγλωσσα MicroLM

- MicroLM Lite
- MicroLM Quality

### Task Specialists

- Coding και Termux specialist
- Mathematics specialist
- Public-research specialist

### Hybrid και Control Models

- Hybrid Router
- Query Planner
- Response Verifier
- Resource Guard
- Adaptive Controller
- Consensus Controller
- Persona Controller
- Context Optimizer
- Confidence Calibrator

Οι controllers είναι μικρά components δρομολόγησης και βαθμολόγησης, όχι μεγάλα transformer LLMs.

## Υβριδικές Λειτουργίες

```text
/υβριδικό auto
/υβριδικό speed
/υβριδικό smart
/υβριδικό quality
/υβριδικό adaptive
/υβριδικό expert
/υβριδικό consensus
/υβριδικό cascade
/υβριδικό off
```

| Λειτουργία | Τρόπος λειτουργίας |
| :--- | :--- |
| `off` | Μόνο ανάκτηση, εργαλεία, specialists και εσωτερική νευρωνική μηχανή |
| `speed` | Ένα πέρασμα με το Fast GGUF |
| `smart` | Επιλογή Fast ή Quality με βάση την ερώτηση και τους ζωντανούς πόρους |
| `quality` | Προτίμηση του Quality GGUF |
| `adaptive` | Δημιουργεί Fast πρόχειρο και παραλείπει το δεύτερο πέρασμα όταν είναι ήδη αρκετά καλό |
| `expert` | Συνδυάζει specialist guidance και βελτιστοποιημένα τοπικά συμφραζόμενα με το Quality μοντέλο |
| `consensus` | Δημιουργεί ανεξάρτητες απαντήσεις Fast και Quality διαδοχικά και επιλέγει την ισχυρότερη |
| `cascade` | Δημιουργεί Fast πρόχειρο, το αποφορτώνει και μετά το ελέγχει/ξαναγράφει με Quality |
| `auto` | Επιλέγει ασφαλή λειτουργία από CPU, RAM, θερμοκρασία, διαθέσιμα μοντέλα και δυσκολία ερώτησης |

Τα Fast και Quality μοντέλα εκτελούνται διαδοχικά. Δεν παραμένουν ταυτόχρονα στη RAM.

## Runtime Modules

Στον φάκελο `Other Files/Modules/` υπάρχουν:

- `persona_engine.py` — μόνιμο όνομα AI και φυσικά δίγλωσσα στυλ
- `context_optimizer.py` — επιλογή σχετικών εγγράφων, μνημών και πρόσφατης συζήτησης
- `consensus_engine.py` — σύγκριση ανεξάρτητων απαντήσεων Fast και Quality
- `confidence_engine.py` — βαθμονόμηση βεβαιότητας απάντησης
- `resource_advisor.py` — εξήγηση επιλογής hardware/model συνδυασμού

## Μόνο Αγγλικά και Ελληνικά

```text
/γλώσσα auto
/γλώσσα en
/γλώσσα el
```

Άλλες γραφές απορρίπτονται πριν εισαχθούν σε training data, μνήμες, έγγραφα ή τοπική παραγωγή.

## Τοπική Μάθηση

### Διδασκαλία απάντησης

```text
/teach Τι είναι το Pocket AI; | Το Pocket AI είναι ένας δίγλωσσος τοπικός βοηθός AI για Termux.
```

### Διόρθωση προηγούμενης απάντησης

```text
/διόρθωση Η σωστή απάντηση είναι αυτή.
```

### Ευρετηρίαση αρχείου ή φακέλου

```text
/ingest ~/storage/downloads/Σημειώσεις
```

### Σύνοψη αρχείου

```text
/σύνοψη ~/storage/downloads/άρθρο.txt
```

### Μόνιμη μνήμη

```text
/θυμήσου project = DedSec Project
```

## Δημόσια Έρευνα και Dork Operators

Η λειτουργία `/dork` ή `/web-learn` χρησιμοποιείται μόνο όταν την εκτελείτε ρητά και χρειάζεται σύνδεση στο διαδίκτυο.

Υποστηρίζονται:

```text
site:
filetype:
intitle:
inurl:
before:
after:
"ακριβής φράση"
-λέξη
```

Μπλοκάρονται ερωτήματα που στοχεύουν εκτεθειμένους κωδικούς, private keys, credentials, admin panels, databases, backups, κάμερες, routers ή ιδιωτικά συστήματα.

## Εγκατάσταση στο Termux

```bash
termux-setup-storage
pkg update -y
pkg install python unzip -y

cd ~
rm -rf Pocket_AI
mkdir Pocket_AI
unzip -o ~/storage/downloads/Pocket_AI.zip -d ~/Pocket_AI

cd ~/Pocket_AI
chmod +x "Other Files/install_models.sh"
bash "Other Files/install_models.sh"

python "Pocket AI.py"
```

Το installer δημιουργεί το συμβατό `llama.cpp` executable. Δεν κατεβάζει τα model weights, επειδή βρίσκονται ήδη στον φάκελο `Models/`.

## Χρήσιμες Εντολές

```text
/βοήθεια
/προσωπικότητα
/όνομα ΟΝΟΜΑ
/στυλ friendly
/ανθρώπινο on
/μοντέλα
/system
/stats
/γιατί
/teach ΕΡΩΤΗΣΗ | ΑΠΑΝΤΗΣΗ
/διόρθωση ΑΠΑΝΤΗΣΗ
/ingest ΔΙΑΔΡΟΜΗ
/σύνοψη ΔΙΑΔΡΟΜΗ
/θυμήσου ΚΛΕΙΔΙ = ΤΙΜΗ
/μνήμες
/ξέχασε ΚΛΕΙΔΙ
/υβριδικό auto
/llm-status
/benchmark
/backup
/έξοδος
```

## Αποθηκευμένα Αρχεία

```text
Other Files/Saved Data/device_profile.json
Other Files/Saved Data/persona.json
Other Files/Saved Data/knowledge.sqlite3
Other Files/Saved Data/dataset.json
Other Files/Saved Data/neural_model.pkl.gz
Other Files/Saved Data/model_metadata.json
Other Files/Saved Data/language_model.pkl.gz
Other Files/Saved Data/backups/
```

## Περιορισμοί

- Το Pocket AI δεν είναι αντίστοιχο ενός σύγχρονου cloud-scale LLM.
- Τα transformer μοντέλα είναι σκόπιμα μικρά για παλιά κινητά.
- Μπορούν να δώσουν λανθασμένες ή ελλιπείς απαντήσεις.
- Σημαντικές ιατρικές, νομικές, οικονομικές, security ή επίκαιρες πληροφορίες χρειάζονται ανεξάρτητη επιβεβαίωση.
- Η ποιότητα Ελληνικών από το κυρίως αγγλόφωνο GGUF μπορεί να είναι χαμηλότερη από τα δίγλωσσα layers ανάκτησης και classifier.
- Ορισμένοι κατασκευαστές κρύβουν πληροφορίες θερμοκρασίας ή SoC, οπότε χρησιμοποιούνται μετρημένα fallbacks.
- Η φυσική συνομιλία αλλάζει μόνο το ύφος. Δεν σημαίνει ότι το πρόγραμμα είναι άνθρωπος, έχει συνείδηση ή συναισθήματα.

## Ιδιωτικότητα

Η βασική συνομιλία, η ανάκτηση γνώσης, οι μνήμες, τα έγγραφα και τα μοντέλα λειτουργούν τοπικά. Δεν απαιτείται cloud API. Πρόσβαση στον δημόσιο ιστό γίνεται μόνο όταν εκτελείτε `/dork` ή `/web-learn`.

Μην αποθηκεύετε μυστικά που δεν πρέπει να υπάρχουν σε μη κρυπτογραφημένα τοπικά δεδομένα εφαρμογής.

## Credits

- Δημιουργός και project: **dedsec1121fk / DedSec Project**
- Ιστοσελίδα: [ded-sec.space](https://ded-sec.space/)
- Sponsors: [GitHub Sponsors](https://github.com/sponsors/dedsec1121fk)
- Τοπικό runtime: `llama.cpp`
- Οι άδειες των bundled models βρίσκονται στο `Other Files/Licenses/`.

## Αποποίηση Ευθύνης

Το Pocket AI παρέχεται για εκπαιδευτική, προσωπική και νόμιμη χρήση ως τοπικός βοηθός. Παρέχεται **ως έχει**, χωρίς εγγύηση ακρίβειας, συμβατότητας ή καταλληλότητας. Ο χρήστης είναι υπεύθυνος να ελέγχει τις παραγόμενες εντολές και απαντήσεις πριν τις χρησιμοποιήσει.
