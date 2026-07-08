<div align="center">
  <img src="https://raw.githubusercontent.com/dedsec1121fk/dedsec1121fk.github.io/47ad8e5cbaaee04af552ae6b90edc49cd75b324b/Assets/Images/Logos/Black%20Purple%20Butterfly%20Logo.jpeg" alt="Pocket AI / DedSec Project Logo" width="150"/>
  <h1>Pocket AI</h1>
  <p><strong>Local bilingual AI for Android + Termux, built for old and low-memory phones</strong></p>
  <p>
    <a href="https://github.com/dedsec1121fk/Pocket-AI"><strong>GitHub Repository</strong></a>
    &nbsp;•&nbsp;
    <a href="https://ded-sec.space/"><strong>DedSec Project Website</strong></a>
  </p>
  <p>
    <a href="https://github.com/sponsors/dedsec1121fk"><img src="https://img.shields.io/badge/Sponsor-DedSec-purple?style=for-the-badge&logo=GitHub" alt="Sponsor DedSec"></a>
  </p>
  <p>
    <img src="https://img.shields.io/badge/Platform-Android%20%7C%20Termux-brightgreen.svg" alt="Android Termux">
    <img src="https://img.shields.io/badge/Root-Not%20Required-blue.svg" alt="No root">
    <img src="https://img.shields.io/badge/Interface-English%20%7C%20Greek-lightgrey.svg" alt="English Greek">
    <img src="https://img.shields.io/badge/Core-Offline-orange.svg" alt="Offline core">
    <img src="https://img.shields.io/badge/School-Grades%201--12-yellow.svg" alt="Grades 1 to 12">
  </p>
</div>

---

<a id="english-readme"></a>

# Pocket AI — English

> **Για να μεταβείτε στην πλήρη Ελληνική έκδοση, συνεχίστε [πατώντας εδώ](#greek-readme).**

**Pocket AI** is a bilingual local assistant for **English and Greek** that runs in **Termux without root**. It combines compact neural classifiers, local GGUF language models, persistent retrieval memory, subject specialists, deterministic school tools, and hardware-aware hybrid routing.

The normal experience is deliberately simple:

```text
Pocket AI is ready. Ask me anything, or type help for options.

You: What is an apple?
Pocket AI: An apple is an edible fruit produced by an apple tree...
```

Type **`help`** at any time to open the easy numbered menu.

<a id="english-table-of-contents"></a>

## Table of Contents

* [Main Features](#main-features)
* [Requirements](#requirements)
* [Installation](#installation)
* [How To Use Pocket AI](#how-to-use-pocket-ai)
* [School Tutor: Grades 1–12](#school-tutor-grades-112)
* [Models And Hybrid Intelligence](#models-and-hybrid-intelligence)
* [Automatic Phone Scanning](#automatic-phone-scanning)
* [Learning From Files And The Web](#learning-from-files-and-the-web)
* [Google AI And API-Key Limitation](#google-ai-and-api-key-limitation)
* [Folder Structure And Save Locations](#folder-structure-and-save-locations)
* [Important Commands](#important-commands)
* [Privacy And Safety](#privacy-and-safety)
* [Limitations](#limitations)
* [Credits](#credits)
* [Disclaimer](#disclaimer)

<a id="main-features"></a>

<details open>
<summary><strong>Main Features</strong></summary>

* **Direct chat by default:** no complicated launcher is required.
* **Simple help:** type `help` or `βοήθεια` to see normal numbered options.
* **English and Greek only:** interface, responses, memories, school knowledge, and web indexing are filtered to the supported languages.
* **Runs without root:** designed for Termux on Android.
* **Works offline:** chatting, local knowledge, mathematics, school help, memories, and bundled models do not require a cloud account.
* **Automatic hardware matching:** scans processor, architecture, total RAM, available RAM, storage, temperature, and model integrity.
* **Low-memory protection:** reduces context, batch size, thread count, output length, or model tier when resources become unsafe.
* **Human-style persona:** give the AI a name and choose Friendly, Calm Expert, Casual, Mentor, or Direct speech.
* **Persistent local memory:** remembers taught answers, user memories, indexed files, settings, and conversation history.
* **Hybrid intelligence:** combines deterministic tools, retrieval, specialists, neural routing, and sequential GGUF passes.
* **School foundation:** shared grade 1–12 support across every model profile.
* **No-key public research:** can learn from safe public search results, Wikipedia, and readable public pages.
* **Safe operator research:** supports public `site:`, `filetype:`, `intitle:`, `inurl:`, `before:`, `after:`, exact phrases, and excluded words.
* **Local file learning:** indexes English and Greek text documents and folders.
* **No TensorFlow, PyTorch, or NumPy required:** the main assistant uses Python’s standard library and bundled files.

</details>

<a id="requirements"></a>

<details>
<summary><strong>Requirements</strong></summary>

| Component | Minimum | Recommended |
| :-- | :-- | :-- |
| **Device** | Android phone/tablet | 64-bit Android phone |
| **Termux** | Current F-Droid build | Current F-Droid build |
| **Root** | Not required | Not required |
| **RAM** | Around 512 MB for the internal engine | 2 GB+ for bundled GGUF inference |
| **Storage** | Enough for Python and the repository | At least 700 MB free for build files, models, and saves |
| **Internet** | Not needed for normal offline chat | Needed only for installation, Git LFS, or explicit web learning |

### Hardware behavior

* 32-bit or severely constrained devices use the internal bilingual engine.
* Approximately 1–2 GB devices prioritize the Q2_K Fast model or internal engine.
* Approximately 3–4 GB devices can use Q4_1 Quality when enough RAM is currently free.
* Stronger devices can use adaptive, expert, consensus, or cascade routing.
* Pocket AI loads only one GGUF process at a time.
* Live RAM and temperature are checked again before an expensive second pass.

</details>

<a id="installation"></a>

<details>
<summary><strong>Installation</strong></summary>

### 1. Install Termux

* Install **Termux from F-Droid** for current package support.
* Open Termux once before running the commands below.
* Allow storage access when Android asks.

### 2. Prepare Termux

```bash
pkg update -y && pkg upgrade -y
pkg install python git git-lfs unzip cmake clang make -y
termux-setup-storage
git lfs install
```

### 3. Clone Pocket AI

```bash
cd ~
git clone https://github.com/dedsec1121fk/Pocket-AI
cd Pocket-AI
git lfs pull
```

### 4. Build the local GGUF runner

The models are already stored inside `Models/`. The installer builds the phone-compatible `llama.cpp` runner; it does not download AI weights.

```bash
chmod +x "Other Files/install_models.sh"
bash "Other Files/install_models.sh"
```

### 5. Start Pocket AI

```bash
python "Pocket AI.py"
```

### Open it later

```bash
cd ~/Pocket-AI && python "Pocket AI.py"
```

</details>

<a id="how-to-use-pocket-ai"></a>

<details>
<summary><strong>How To Use Pocket AI</strong></summary>

Pocket AI opens directly into chat:

```text
You: What is gravity?
Pocket AI: Gravity is the attraction between objects with mass...
```

You can type normal questions instead of commands:

* `What is an apple?`
* `Explain photosynthesis.`
* `What is 25% of 80?`
* `Solve 2*x + 3 = 11.`
* `Explain democracy.`
* `Grade 5 math topics.`
* `Τι είναι η βαρύτητα;`
* `Πόσο κάνει 12*7;`
* `Εξήγησε τη φωτοσύνθεση.`
* `Τάξη 9 επιστήμη.`

Type one of these to open the easy menu:

* `help`
* `/help`
* `βοήθεια`
* `/βοήθεια`

The easy menu includes:

1. Return to chat
2. Scan the phone and select the best model
3. Change the AI name and speaking style
4. Teach one question and answer
5. Learn from a file or folder
6. Safely research the public web and learn
7. Open the grade 1–12 school tutor
8. Show the active model and status
9. Show advanced commands
10. Exit

</details>

<a id="school-tutor-grades-112"></a>

<details open>
<summary><strong>School Tutor: Grades 1–12</strong></summary>

The school foundation is **shared across every model profile**. This means the internal engine, Fast GGUF, Quality GGUF, and hybrid modes all use the same school tools before generic language-model fallback.

### Covered school areas

* **Mathematics**
  * counting and place value
  * addition, subtraction, multiplication, and division
  * fractions, decimals, percentages, ratios, and proportions
  * factors, multiples, GCD, and LCM
  * integers, exponents, and scientific notation
  * algebra and linear equations
  * quadratic equations
  * coordinates and linear functions
  * geometry, perimeter, area, circles, volume, and Pythagorean theorem
  * mean, median, mode, range, statistics, and probability
  * trigonometry, functions, vectors, and introductory calculus
* **Science**
  * living things, plants, animals, ecosystems, and human body systems
  * matter, atoms, elements, periodic table, reactions, acids, and bases
  * cells, DNA, genetics, evolution, and ecology
  * forces, motion, Newton’s laws, energy, electricity, circuits, and waves
  * weather, climate, rocks, water cycle, Earth systems, and Solar System
  * scientific method and evidence
* **English and Greek language**
  * sentences, subjects, predicates, and parts of speech
  * verb tenses and grammar
  * paragraph and essay structure
  * summaries, vocabulary, argumentation, and evidence
  * literary devices and literature analysis
  * research writing, sources, citations, and plagiarism awareness
* **History, Geography, and Civics**
  * maps, directions, continents, oceans, landforms, and population
  * Ancient Greece, Ancient Rome, Byzantium, Renaissance, and Industrial Revolution
  * World Wars and modern history foundations
  * democracy, constitutions, rights, duties, institutions, and citizenship
  * economics, scarcity, opportunity cost, supply, and demand
  * introductory philosophy and logic
* **Computing and study skills**
  * hardware, software, input, output, and storage
  * algorithms, variables, conditions, loops, functions, testing, and debugging
  * digital safety, source reliability, and media literacy
  * active recall, spaced repetition, worked examples, and study planning

### Deterministic math support

Pocket AI solves many common school calculations without asking a language model to guess:

```text
What is 25% of 80?
1/2 + 1/3
Mean of 5, 8, 8, 10
GCD of 24 and 36
Solve 2*x + 3 = 11
Solve x^2 - 5*x + 6 = 0
Area of a rectangle length 8 width 3
Area of a circle radius 5
```

### Grade overviews

```text
/school 5 math
/school 9 science
/school 12 computing
```

Greek examples:

```text
/school 5 μαθηματικά
/school 9 επιστήμες
/school 12 πληροφορική
```

> The school pack is a broad bilingual learning foundation. It does not claim to contain every national textbook, examination board, or teacher’s exact curriculum.

</details>

<a id="models-and-hybrid-intelligence"></a>

<details>
<summary><strong>Models And Hybrid Intelligence</strong></summary>

### Bundled GGUF language models

* **SmolLM2-135M-Instruct Q2_K Fast**
  * lowest bundled GGUF memory requirement
  * intended for old and 2 GB-class phones
  * used for quick drafts and low-resource answers
* **SmolLM2-135M-Instruct Q4_1 Quality**
  * higher-quality quantization of the same compact model family
  * selected when current RAM, CPU, storage, and temperature permit it
  * used for quality answers, verification, and consensus

### Pre-trained bilingual neural profiles

* Micro
* Lite
* Balanced
* Standard
* Max

### General specialists

* Coding and Termux specialist
* Mathematics specialist
* Public research specialist

### School specialists

* School Mathematics Specialist
* School Science Specialist
* School Language Specialist
* School Humanities Specialist
* School Computing and Study Specialist
* Grade 1–12 School Knowledge Foundation
* School Hybrid Controller

### Hybrid controllers

* Query planner
* Hybrid router
* Resource guard
* Context optimizer
* Confidence calibrator
* Response verifier
* Adaptive controller
* Consensus controller
* Persona controller
* No-key web-learning controller

### Hybrid modes

* **Off:** internal tools, memory, retrieval, and specialists only
* **Speed:** quickest safe single-pass model
* **Smart:** routes each question automatically
* **Quality:** prefers the higher-quality model when safe
* **Adaptive:** starts fast and performs a second pass only when useful
* **Expert:** combines specialist guidance, optimized context, and quality inference
* **Consensus:** compares independent Fast and Quality answers sequentially
* **Cascade:** generates a draft, unloads it, then verifies and rewrites it
* **Auto:** chooses the safest useful mode from live phone resources

Commands:

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

</details>

<a id="automatic-phone-scanning"></a>

<details>
<summary><strong>Automatic Phone Scanning</strong></summary>

Pocket AI checks:

* phone manufacturer and model
* Android hardware and board identifiers
* known Qualcomm, MediaTek, Exynos, Unisoc, Kirin, Tensor, Tegra, Rockchip, Allwinner, Amlogic, and x86 naming patterns
* fallback benchmark for unknown processors
* ARM, ARM64, x86, or x86-64 architecture
* 32-bit or 64-bit Termux userspace
* logical cores and frequency clusters
* total RAM and currently available RAM
* application storage and shared storage
* battery and thermal information when exposed by Android
* bundled model presence, file size, GGUF header, and checksum

The scan selects:

* neural classifier profile
* internal, Fast, or Quality inference
* hybrid mode
* CPU thread count
* context size
* batch and micro-batch sizes
* answer-token limit
* timeout and emergency fallback behavior

Run a scan manually:

```text
scan my phone
```

or:

```text
/scan-phone
```

</details>

<a id="learning-from-files-and-the-web"></a>

<details>
<summary><strong>Learning From Files And The Web</strong></summary>

### Learn from a file or folder

```text
/ingest ~/storage/downloads/SchoolNotes
```

Pocket AI can:

* read supported English and Greek text files
* split them into searchable knowledge chunks
* store source paths
* retrieve relevant passages during later questions
* summarize readable text files

### Teach a direct answer

```text
/teach What is Pocket AI? | Pocket AI is a local bilingual Termux assistant.
```

### No-key public web learning

```text
/web-learn photosynthesis for middle school
/dork site:python.org sqlite tutorial
/dork "Pythagorean theorem" filetype:html
```

The no-key learning pipeline uses:

* **Bing RSS search results**
* **Wikipedia MediaWiki search API**
* **readable public HTTP/HTTPS pages**
* source-aware local indexing
* English/Greek content filtering
* conservative request limits
* `robots.txt` checks for fetched pages

Blocked research includes queries aimed at:

* exposed passwords or API keys
* private keys and credential files
* database backups
* login/admin panels
* private or local hosts
* cameras, routers, or exposed devices
* executable files, archives, databases, and key containers

</details>

<a id="google-ai-and-api-key-limitation"></a>

<details>
<summary><strong>Google AI And API-Key Limitation</strong></summary>

Pocket AI does **not** claim to access Google Gemini anonymously.

* The official Gemini API requires authentication credentials.
* Google’s official programmable search API also requires configuration and an API key.
* Pocket AI does not bypass authentication, scrape private AI sessions, or imitate Google services.
* Without a key, Pocket AI uses its bundled local models plus the public no-key research sources listed above.
* Type `/google-ai` inside Pocket AI to see this explanation.

This design keeps the project honest, reproducible, and usable without attaching a cloud billing account.

</details>

<a id="folder-structure-and-save-locations"></a>

<details>
<summary><strong>Folder Structure And Save Locations</strong></summary>

```text
Pocket-AI/
├── Pocket AI.py
├── README.md
├── Models/
│   ├── GGUF language models
│   ├── pre-trained neural profiles
│   ├── bilingual generators
│   ├── general specialists
│   ├── school specialists
│   └── hybrid controllers
└── Other Files/
    ├── Modules/
    ├── Documentation/
    ├── Licenses/
    ├── Saved Data/
    ├── CHECKSUMS.sha256
    └── install_models.sh
```

Generated user data is kept under:

```text
Other Files/Saved Data/
```

That folder may contain:

* selected hardware profile
* AI name and persona
* model settings
* SQLite knowledge database
* memories and taught answers
* indexed file and web knowledge
* local conversation history
* exports and backups
* compiled `llama.cpp` runner files

Bundled model files remain separate under `Models/`.

</details>

<a id="important-commands"></a>

<details>
<summary><strong>Important Commands</strong></summary>

### Easy controls

* `help` — open the simple numbered menu
* `exit` — close Pocket AI
* `scan my phone` — select the best model automatically
* `change your name` — open persona configuration
* `school help` — show school coverage

### Identity and language

* `/name NAME`
* `/style friendly|calm_expert|casual|mentor|direct`
* `/human on|off`
* `/language auto|en|el`

### School

* `/school`
* `/school 5 math`
* `/school 9 science`
* `/school 12 computing`

### Learning

* `/teach QUESTION | ANSWER`
* `/correct ANSWER`
* `/ingest PATH`
* `/summarize PATH`
* `/web-learn QUERY`
* `/dork QUERY`
* `/remember KEY = VALUE`

### Models

* `/models`
* `/stats`
* `/system`
* `/llm-status`
* `/llm off|fallback|always`
* `/llm-model fast|quality`
* `/hybrid MODE`
* `/cpu-profile auto|ultra_eco|eco|entry|balanced|performance`

### Maintenance

* `/history`
* `/clear-history`
* `/export`
* `/backup`
* `/benchmark`
* `/why`
* `/debug`

</details>

<a id="privacy-and-safety"></a>

<details>
<summary><strong>Privacy And Safety</strong></summary>

* Normal chat runs locally.
* Memories, history, files, and learned knowledge remain in the local save folder unless the user exports or uploads them.
* Web access happens only when the user explicitly requests web learning or runs installation/update commands.
* The web learner accepts only public HTTP/HTTPS targets.
* Local, private, `.onion`, and non-public hosts are blocked.
* The dork validator blocks credential hunting, exposed systems, private files, databases, and admin-interface targeting.
* Download size, file type, language, and page count are limited.
* Pocket AI does not guarantee that public web content is correct; retrieved information should be checked against reliable sources.

</details>

<a id="limitations"></a>

<details>
<summary><strong>Limitations</strong></summary>

* Pocket AI is not ChatGPT, Gemini, or another cloud-scale model.
* The bundled 135M models are intentionally small so they can run on older phones.
* Smaller models can misunderstand questions or produce incorrect text.
* The school layer is broad but not a complete copy of every country’s official curriculum.
* It should not replace a teacher, textbook, doctor, lawyer, financial professional, or emergency service.
* Automatic hardware thresholds are conservative estimates; Android background load varies by phone and firmware.
* Public web learning can fail because of connectivity, robots rules, changed websites, or provider limits.
* Learned web content may be outdated, incomplete, biased, or wrong.
* Always verify important facts and calculations.

</details>

<a id="credits"></a>

<details>
<summary><strong>Credits</strong></summary>

* **Creator:** dedsec1121fk
* **Project:** Pocket AI / DedSec Project
* **Platform:** Android + Termux
* **Languages:** English and Greek
* **Local model runtime:** `llama.cpp`
* **Bundled compact language-model family:** SmolLM2
* **GitHub:** [dedsec1121fk/Pocket-AI](https://github.com/dedsec1121fk/Pocket-AI)
* **Website:** [ded-sec.space](https://ded-sec.space)
* **Sponsors:** [GitHub Sponsors](https://github.com/sponsors/dedsec1121fk)

</details>

<a id="disclaimer"></a>

<details>
<summary><strong>Disclaimer</strong></summary>

Pocket AI is provided for educational, personal, and experimental use. It is provided **AS IS**, without guarantees of accuracy, availability, suitability, or fitness for a particular purpose. The creator and contributors are not responsible for damage, data loss, incorrect decisions, overheating, battery drain, account restrictions, or other consequences caused by use or misuse.

Use web learning only for lawful public research. Respect website terms, copyright, privacy, robots rules, and applicable law. Do not use search operators to target credentials, private systems, exposed devices, or data that you are not authorized to access.

</details>

---

<a id="greek-readme"></a>

# Pocket AI — Ελληνικά

> **To return to the complete English version, continue by [clicking here](#english-readme).**

Το **Pocket AI** είναι ένας δίγλωσσος τοπικός βοηθός για **Αγγλικά και Ελληνικά**, σχεδιασμένος για **Termux χωρίς root**. Συνδυάζει μικρούς νευρωνικούς classifiers, τοπικά μοντέλα GGUF, μόνιμη μνήμη ανάκτησης, ειδικά μοντέλα μαθημάτων, ντετερμινιστικά σχολικά εργαλεία και υβριδική δρομολόγηση που προσαρμόζεται στο κινητό.

Η κανονική χρήση είναι απλή:

```text
Pocket AI είναι έτοιμο. Ρώτησέ με οτιδήποτε ή γράψε βοήθεια για επιλογές.

Εσύ: Τι είναι το μήλο;
Pocket AI: Το μήλο είναι ένας βρώσιμος καρπός της μηλιάς...
```

Γράψε **`βοήθεια`** οποιαδήποτε στιγμή για να ανοίξει το απλό αριθμημένο μενού.

<a id="greek-table-of-contents"></a>

## Περιεχόμενα

* [Κύρια Χαρακτηριστικά](#κύρια-χαρακτηριστικά)
* [Απαιτήσεις](#απαιτήσεις)
* [Εγκατάσταση](#εγκατάσταση)
* [Πώς Χρησιμοποιείται](#πώς-χρησιμοποιείται)
* [Σχολικός Βοηθός: Τάξεις 1–12](#σχολικός-βοηθός-τάξεις-112)
* [Μοντέλα και Υβριδική Νοημοσύνη](#μοντέλα-και-υβριδική-νοημοσύνη)
* [Αυτόματη Σάρωση Κινητού](#αυτόματη-σάρωση-κινητού)
* [Μάθηση από Αρχεία και Διαδίκτυο](#μάθηση-από-αρχεία-και-διαδίκτυο)
* [Google AI και Περιορισμός API Key](#google-ai-και-περιορισμός-api-key)
* [Δομή Φακέλων και Αποθηκεύσεις](#δομή-φακέλων-και-αποθηκεύσεις)
* [Σημαντικές Εντολές](#σημαντικές-εντολές)
* [Ιδιωτικότητα και Ασφάλεια](#ιδιωτικότητα-και-ασφάλεια)
* [Περιορισμοί](#περιορισμοί)
* [Συντελεστές](#συντελεστές)
* [Αποποίηση Ευθύνης](#αποποίηση-ευθύνης)

<a id="κύρια-χαρακτηριστικά"></a>

<details open>
<summary><strong>Κύρια Χαρακτηριστικά</strong></summary>

* **Άμεση συνομιλία:** δεν απαιτείται περίπλοκος launcher.
* **Απλή βοήθεια:** γράψε `help` ή `βοήθεια` για κανονικές αριθμημένες επιλογές.
* **Μόνο Αγγλικά και Ελληνικά:** interface, απαντήσεις, μνήμες, σχολική γνώση και ευρετηρίαση ιστού φιλτράρονται στις δύο γλώσσες.
* **Χωρίς root:** σχεδιασμένο για Termux σε Android.
* **Λειτουργία offline:** συνομιλία, τοπική γνώση, μαθηματικά, σχολική βοήθεια, μνήμες και ενσωματωμένα μοντέλα δεν χρειάζονται cloud λογαριασμό.
* **Αυτόματη αντιστοίχιση hardware:** ελέγχει επεξεργαστή, αρχιτεκτονική, συνολική και διαθέσιμη RAM, αποθήκευση, θερμοκρασία και ακεραιότητα μοντέλων.
* **Προστασία χαμηλής RAM:** μειώνει context, batch, threads, μήκος απάντησης ή βαθμίδα μοντέλου όταν χρειάζεται.
* **Ανθρώπινο στυλ:** δώσε όνομα στο AI και επίλεξε Friendly, Calm Expert, Casual, Mentor ή Direct.
* **Μόνιμη τοπική μνήμη:** κρατά διδαγμένες απαντήσεις, μνήμες, αρχεία, ρυθμίσεις και ιστορικό.
* **Υβριδική νοημοσύνη:** συνδυάζει εργαλεία, retrieval, specialists, neural routing και διαδοχικά GGUF περάσματα.
* **Σχολική βάση:** κοινή υποστήριξη τάξεων 1–12 για κάθε profile μοντέλου.
* **Δημόσια έρευνα χωρίς API key:** μάθηση από ασφαλή δημόσια αποτελέσματα, Wikipedia και αναγνώσιμες δημόσιες σελίδες.
* **Ασφαλείς τελεστές αναζήτησης:** `site:`, `filetype:`, `intitle:`, `inurl:`, `before:`, `after:`, ακριβείς φράσεις και εξαιρούμενες λέξεις.
* **Μάθηση από τοπικά αρχεία:** ευρετηρίαση αγγλικών και ελληνικών εγγράφων και φακέλων.
* **Χωρίς απαίτηση TensorFlow, PyTorch ή NumPy:** ο βασικός βοηθός χρησιμοποιεί standard library και ενσωματωμένα αρχεία.

</details>

<a id="απαιτήσεις"></a>

<details>
<summary><strong>Απαιτήσεις</strong></summary>

| Στοιχείο | Ελάχιστο | Προτεινόμενο |
| :-- | :-- | :-- |
| **Συσκευή** | Android κινητό ή tablet | 64-bit Android κινητό |
| **Termux** | Σύγχρονη έκδοση από F-Droid | Σύγχρονη έκδοση από F-Droid |
| **Root** | Δεν απαιτείται | Δεν απαιτείται |
| **RAM** | Περίπου 512 MB για τον εσωτερικό engine | 2 GB+ για GGUF inference |
| **Αποθήκευση** | Αρκετή για Python και repository | Τουλάχιστον 700 MB ελεύθερα για build, μοντέλα και saves |
| **Internet** | Δεν χρειάζεται για κανονικό offline chat | Χρειάζεται μόνο για εγκατάσταση, Git LFS ή ρητή web learning λειτουργία |

### Συμπεριφορά ανά hardware

* 32-bit ή πολύ περιορισμένες συσκευές χρησιμοποιούν τον εσωτερικό δίγλωσσο engine.
* Συσκευές περίπου 1–2 GB προτιμούν Q2_K Fast ή εσωτερικό engine.
* Συσκευές περίπου 3–4 GB μπορούν να χρησιμοποιήσουν Q4_1 Quality όταν υπάρχει αρκετή διαθέσιμη RAM.
* Ισχυρότερες συσκευές μπορούν να χρησιμοποιήσουν adaptive, expert, consensus ή cascade.
* Φορτώνεται μόνο μία διεργασία GGUF κάθε φορά.
* Η RAM και η θερμοκρασία ελέγχονται ξανά πριν από ακριβό δεύτερο πέρασμα.

</details>

<a id="εγκατάσταση"></a>

<details>
<summary><strong>Εγκατάσταση</strong></summary>

### 1. Εγκατάσταση Termux

* Εγκατέστησε το **Termux από F-Droid**.
* Άνοιξε το Termux μία φορά πριν εκτελέσεις τις εντολές.
* Επίτρεψε πρόσβαση αποθήκευσης όταν ζητηθεί.

### 2. Προετοιμασία Termux

```bash
pkg update -y && pkg upgrade -y
pkg install python git git-lfs unzip cmake clang make -y
termux-setup-storage
git lfs install
```

### 3. Κλωνοποίηση Pocket AI

```bash
cd ~
git clone https://github.com/dedsec1121fk/Pocket-AI
cd Pocket-AI
git lfs pull
```

### 4. Δημιουργία τοπικού GGUF runner

Τα μοντέλα βρίσκονται ήδη στο `Models/`. Ο installer δημιουργεί τον συμβατό `llama.cpp` runner και δεν κατεβάζει AI weights.

```bash
chmod +x "Other Files/install_models.sh"
bash "Other Files/install_models.sh"
```

### 5. Εκκίνηση

```bash
python "Pocket AI.py"
```

### Άνοιγμα αργότερα

```bash
cd ~/Pocket-AI && python "Pocket AI.py"
```

</details>

<a id="πώς-χρησιμοποιείται"></a>

<details>
<summary><strong>Πώς Χρησιμοποιείται</strong></summary>

Το Pocket AI ανοίγει απευθείας στη συνομιλία:

```text
Εσύ: Τι είναι η βαρύτητα;
Pocket AI: Η βαρύτητα είναι η έλξη μεταξύ αντικειμένων που έχουν μάζα...
```

Μπορείς να γράψεις φυσιολογικές ερωτήσεις:

* `Τι είναι το μήλο;`
* `Εξήγησε τη φωτοσύνθεση.`
* `Πόσο είναι το 25% του 80;`
* `Λύσε 2*x + 3 = 11.`
* `Εξήγησε τη δημοκρατία.`
* `Τάξη 5 μαθηματικά.`
* `What is gravity?`
* `What is 12*7?`
* `Explain photosynthesis.`
* `Grade 9 science.`

Για το απλό μενού γράψε:

* `help`
* `/help`
* `βοήθεια`
* `/βοήθεια`

Το μενού περιλαμβάνει:

1. Επιστροφή στη συνομιλία
2. Σάρωση κινητού και επιλογή καλύτερου μοντέλου
3. Αλλαγή ονόματος και στυλ ομιλίας
4. Διδασκαλία ερώτησης και απάντησης
5. Μάθηση από αρχείο ή φάκελο
6. Ασφαλής δημόσια έρευνα και μάθηση
7. Σχολικός βοηθός τάξεων 1–12
8. Προβολή ενεργού μοντέλου και κατάστασης
9. Προβολή προχωρημένων εντολών
10. Έξοδος

</details>

<a id="σχολικός-βοηθός-τάξεις-112"></a>

<details open>
<summary><strong>Σχολικός Βοηθός: Τάξεις 1–12</strong></summary>

Η σχολική βάση είναι **κοινή για κάθε profile μοντέλου**. Ο εσωτερικός engine, το Fast GGUF, το Quality GGUF και τα hybrid modes χρησιμοποιούν τα ίδια σχολικά εργαλεία πριν από γενικό LLM fallback.

### Καλυπτόμενοι τομείς

* **Μαθηματικά**
  * μέτρηση και αξία θέσης
  * πρόσθεση, αφαίρεση, πολλαπλασιασμός και διαίρεση
  * κλάσματα, δεκαδικοί, ποσοστά, λόγοι και αναλογίες
  * παράγοντες, πολλαπλάσια, ΜΚΔ και ΕΚΠ
  * ακέραιοι, δυνάμεις και επιστημονική γραφή
  * άλγεβρα και γραμμικές εξισώσεις
  * εξισώσεις δευτέρου βαθμού
  * συντεταγμένες και γραμμικές συναρτήσεις
  * γεωμετρία, περίμετρος, εμβαδόν, κύκλοι, όγκος και Πυθαγόρειο θεώρημα
  * μέσος όρος, διάμεσος, επικρατούσα τιμή, εύρος, στατιστική και πιθανότητες
  * τριγωνομετρία, συναρτήσεις, διανύσματα και εισαγωγικός λογισμός
* **Επιστήμες**
  * ζωντανά, φυτά, ζώα, οικοσυστήματα και ανθρώπινο σώμα
  * ύλη, άτομα, στοιχεία, περιοδικός πίνακας, αντιδράσεις, οξέα και βάσεις
  * κύτταρα, DNA, γενετική, εξέλιξη και οικολογία
  * δυνάμεις, κίνηση, νόμοι Νεύτωνα, ενέργεια, ηλεκτρισμός, κυκλώματα και κύματα
  * καιρός, κλίμα, πετρώματα, κύκλος νερού, Γη και Ηλιακό Σύστημα
  * επιστημονική μέθοδος και τεκμήρια
* **Ελληνική και Αγγλική γλώσσα**
  * προτάσεις, υποκείμενο, κατηγόρημα και μέρη του λόγου
  * χρόνοι ρημάτων και γραμματική
  * δομή παραγράφου και έκθεσης
  * περιλήψεις, λεξιλόγιο, επιχειρηματολογία και τεκμήρια
  * λογοτεχνικά σχήματα και ανάλυση λογοτεχνίας
  * έρευνα, πηγές, παραπομπές και αποφυγή λογοκλοπής
* **Ιστορία, Γεωγραφία και Αγωγή Πολίτη**
  * χάρτες, κατευθύνσεις, ήπειροι, ωκεανοί, ανάγλυφο και πληθυσμός
  * Αρχαία Ελλάδα, Αρχαία Ρώμη, Βυζάντιο, Αναγέννηση και Βιομηχανική Επανάσταση
  * Παγκόσμιοι Πόλεμοι και βασικές έννοιες νεότερης ιστορίας
  * δημοκρατία, σύνταγμα, δικαιώματα, υποχρεώσεις, θεσμοί και πολίτες
  * οικονομικά, σπανιότητα, κόστος ευκαιρίας, προσφορά και ζήτηση
  * εισαγωγή σε φιλοσοφία και λογική
* **Πληροφορική και δεξιότητες μελέτης**
  * hardware, software, είσοδος, έξοδος και αποθήκευση
  * αλγόριθμοι, μεταβλητές, συνθήκες, βρόχοι, συναρτήσεις, testing και debugging
  * ψηφιακή ασφάλεια, αξιοπιστία πηγών και media literacy
  * ενεργή ανάκληση, κατανεμημένη επανάληψη, λυμένα παραδείγματα και πρόγραμμα μελέτης

### Ντετερμινιστικά μαθηματικά

```text
Πόσο είναι το 25% του 80;
1/2 + 1/3
Μέσος όρος των 5, 8, 8, 10
ΜΚΔ των 24 και 36
Λύσε 2*x + 3 = 11
Λύσε x^2 - 5*x + 6 = 0
Εμβαδόν ορθογωνίου μήκος 8 πλάτος 3
Εμβαδόν κύκλου ακτίνα 5
```

### Προβολή ύλης ανά τάξη

```text
/school 5 μαθηματικά
/school 9 επιστήμες
/school 12 πληροφορική
```

> Η σχολική βάση είναι ευρεία δίγλωσση βοήθεια. Δεν ισχυρίζεται ότι περιέχει κάθε επίσημο σχολικό βιβλίο, εξεταστικό οργανισμό ή ακριβές πρόγραμμα κάθε χώρας.

</details>

<a id="μοντέλα-και-υβριδική-νοημοσύνη"></a>

<details>
<summary><strong>Μοντέλα και Υβριδική Νοημοσύνη</strong></summary>

### Ενσωματωμένα GGUF μοντέλα

* **SmolLM2-135M-Instruct Q2_K Fast**
  * χαμηλότερη απαίτηση RAM
  * για παλιά και 2 GB-class κινητά
  * για γρήγορα drafts και low-resource απαντήσεις
* **SmolLM2-135M-Instruct Q4_1 Quality**
  * καλύτερη quantization της ίδιας compact οικογένειας
  * επιλέγεται όταν RAM, CPU, storage και θερμοκρασία το επιτρέπουν
  * για quality απαντήσεις, verification και consensus

### Προεκπαιδευμένα δίγλωσσα neural profiles

* Micro
* Lite
* Balanced
* Standard
* Max

### Γενικά specialist μοντέλα

* Coding και Termux
* Μαθηματικά
* Δημόσια έρευνα

### Σχολικά specialist μοντέλα

* Σχολικά Μαθηματικά
* Σχολικές Επιστήμες
* Σχολική Γλώσσα
* Σχολικές Ανθρωπιστικές Επιστήμες
* Σχολική Πληροφορική και Μελέτη
* Σχολική Βάση Γνώσης Τάξεων 1–12
* School Hybrid Controller

### Hybrid controllers

* Query planner
* Hybrid router
* Resource guard
* Context optimizer
* Confidence calibrator
* Response verifier
* Adaptive controller
* Consensus controller
* Persona controller
* No-key web-learning controller

### Hybrid modes

* **Off:** μόνο εσωτερικά εργαλεία, μνήμη, retrieval και specialists
* **Speed:** γρηγορότερο ασφαλές single pass
* **Smart:** αυτόματη δρομολόγηση ανά ερώτηση
* **Quality:** προτίμηση καλύτερου μοντέλου όταν είναι ασφαλές
* **Adaptive:** δεύτερο pass μόνο όταν χρειάζεται
* **Expert:** specialist guidance, optimized context και quality inference
* **Consensus:** σύγκριση ανεξάρτητων Fast και Quality απαντήσεων
* **Cascade:** draft, unload, verification και rewrite
* **Auto:** επιλογή από τη ζωντανή κατάσταση του κινητού

</details>

<a id="αυτόματη-σάρωση-κινητού"></a>

<details>
<summary><strong>Αυτόματη Σάρωση Κινητού</strong></summary>

Ελέγχονται:

* κατασκευαστής και μοντέλο κινητού
* hardware, board και SoC identifiers
* γνωστά Qualcomm, MediaTek, Exynos, Unisoc, Kirin, Tensor, Tegra, Rockchip, Allwinner, Amlogic και x86 patterns
* benchmark για άγνωστους επεξεργαστές
* ARM, ARM64, x86 ή x86-64
* 32-bit ή 64-bit Termux userspace
* πυρήνες και συχνότητες CPU
* συνολική και διαθέσιμη RAM
* αποθήκευση εφαρμογής και shared storage
* θερμοκρασία και battery δεδομένα όταν παρέχονται από Android
* παρουσία, μέγεθος, GGUF header και checksum μοντέλων

Η σάρωση επιλέγει:

* neural classifier profile
* internal, Fast ή Quality inference
* hybrid mode
* threads
* context
* batch και micro-batch
* όριο tokens
* timeout και emergency fallback

Για χειροκίνητη σάρωση:

```text
scan my phone
```

</details>

<a id="μάθηση-από-αρχεία-και-διαδίκτυο"></a>

<details>
<summary><strong>Μάθηση από Αρχεία και Διαδίκτυο</strong></summary>

### Μάθηση από αρχείο ή φάκελο

```text
/ingest ~/storage/downloads/SchoolNotes
```

Το Pocket AI μπορεί να:

* διαβάζει υποστηριζόμενα αγγλικά και ελληνικά text files
* τα χωρίζει σε searchable knowledge chunks
* κρατά source paths
* ανακτά σχετικά αποσπάσματα σε επόμενες ερωτήσεις
* δημιουργεί extractive summaries

### Άμεση διδασκαλία

```text
/teach Τι είναι το Pocket AI; | Το Pocket AI είναι τοπικός δίγλωσσος βοηθός Termux.
```

### Δημόσια web learning χωρίς API key

```text
/web-learn φωτοσύνθεση για γυμνάσιο
/dork site:python.org sqlite tutorial
/dork "Πυθαγόρειο θεώρημα" filetype:html
```

Χρησιμοποιούνται:

* **Bing RSS search results**
* **Wikipedia MediaWiki API**
* **αναγνώσιμες δημόσιες HTTP/HTTPS σελίδες**
* source-aware local indexing
* φιλτράρισμα Αγγλικών και Ελληνικών
* συντηρητικά request limits
* έλεγχοι `robots.txt`

Μπλοκάρονται έρευνες για:

* εκτεθειμένους κωδικούς ή API keys
* private keys και credential files
* database backups
* login/admin panels
* private ή local hosts
* cameras, routers ή εκτεθειμένες συσκευές
* executables, archives, databases και key containers

</details>

<a id="google-ai-και-περιορισμός-api-key"></a>

<details>
<summary><strong>Google AI και Περιορισμός API Key</strong></summary>

Το Pocket AI **δεν ισχυρίζεται** ότι χρησιμοποιεί ανώνυμα το Google Gemini.

* Το επίσημο Gemini API απαιτεί authentication credentials.
* Το επίσημο programmable search API της Google επίσης απαιτεί ρύθμιση και API key.
* Το Pocket AI δεν παρακάμπτει authentication και δεν αντιγράφει private AI sessions.
* Χωρίς key χρησιμοποιεί τα ενσωματωμένα τοπικά μοντέλα και τις δημόσιες no-key πηγές που αναφέρονται παραπάνω.
* Γράψε `/google-ai` μέσα στο Pocket AI για την ίδια εξήγηση.

</details>

<a id="δομή-φακέλων-και-αποθηκεύσεις"></a>

<details>
<summary><strong>Δομή Φακέλων και Αποθηκεύσεις</strong></summary>

```text
Pocket-AI/
├── Pocket AI.py
├── README.md
├── Models/
│   ├── GGUF μοντέλα
│   ├── neural profiles
│   ├── bilingual generators
│   ├── general specialists
│   ├── school specialists
│   └── hybrid controllers
└── Other Files/
    ├── Modules/
    ├── Documentation/
    ├── Licenses/
    ├── Saved Data/
    ├── CHECKSUMS.sha256
    └── install_models.sh
```

Τα δεδομένα χρήστη αποθηκεύονται στο:

```text
Other Files/Saved Data/
```

Μπορεί να περιλαμβάνονται:

* hardware profile
* όνομα και persona AI
* model settings
* SQLite knowledge database
* μνήμες και taught answers
* γνώση από αρχεία και web
* τοπικό ιστορικό συνομιλιών
* exports και backups
* compiled `llama.cpp` runner

</details>

<a id="σημαντικές-εντολές"></a>

<details>
<summary><strong>Σημαντικές Εντολές</strong></summary>

### Απλές εντολές

* `βοήθεια` — άνοιγμα απλού μενού
* `έξοδος` — κλείσιμο
* `scan my phone` — αυτόματη επιλογή μοντέλου
* `change your name` — ρυθμίσεις persona
* `school help` — σχολική κάλυψη

### Ταυτότητα και γλώσσα

* `/όνομα ΟΝΟΜΑ`
* `/στυλ friendly|calm_expert|casual|mentor|direct`
* `/ανθρώπινο on|off`
* `/γλώσσα auto|en|el`

### Σχολείο

* `/school`
* `/school 5 μαθηματικά`
* `/school 9 επιστήμες`
* `/school 12 πληροφορική`

### Μάθηση

* `/teach ΕΡΩΤΗΣΗ | ΑΠΑΝΤΗΣΗ`
* `/διόρθωση ΑΠΑΝΤΗΣΗ`
* `/ingest ΔΙΑΔΡΟΜΗ`
* `/σύνοψη ΔΙΑΔΡΟΜΗ`
* `/web-learn ΕΡΩΤΗΜΑ`
* `/dork ΕΡΩΤΗΜΑ`
* `/remember ΚΛΕΙΔΙ = ΤΙΜΗ`

### Μοντέλα

* `/μοντέλα`
* `/stats`
* `/system`
* `/llm-status`
* `/llm off|fallback|always`
* `/μοντέλο fast|quality`
* `/υβριδικό MODE`
* `/επεξεργαστής auto|ultra_eco|eco|entry|balanced|performance`

### Συντήρηση

* `/history`
* `/clear-history`
* `/export`
* `/backup`
* `/benchmark`
* `/why`
* `/debug`

</details>

<a id="ιδιωτικότητα-και-ασφάλεια"></a>

<details>
<summary><strong>Ιδιωτικότητα και Ασφάλεια</strong></summary>

* Η κανονική συνομιλία εκτελείται τοπικά.
* Μνήμες, ιστορικό, αρχεία και γνώση παραμένουν στον τοπικό save folder εκτός αν τα εξαγάγει ή ανεβάσει ο χρήστης.
* Web access γίνεται μόνο όταν ζητηθεί ρητά web learning ή installation/update.
* Επιτρέπονται μόνο δημόσιοι HTTP/HTTPS στόχοι.
* Local, private, `.onion` και μη δημόσιοι hosts μπλοκάρονται.
* Ο dork validator μπλοκάρει credential hunting, exposed systems, private files, databases και admin targets.
* Περιορίζονται μέγεθος download, file type, γλώσσα και αριθμός σελίδων.
* Το Pocket AI δεν εγγυάται ότι δημόσιο web content είναι σωστό.

</details>

<a id="περιορισμοί"></a>

<details>
<summary><strong>Περιορισμοί</strong></summary>

* Το Pocket AI δεν είναι ChatGPT, Gemini ή cloud-scale μοντέλο.
* Τα ενσωματωμένα 135M μοντέλα είναι μικρά για να λειτουργούν σε παλιά κινητά.
* Μπορεί να παρερμηνεύσουν ερωτήσεις ή να παράγουν λάθος κείμενο.
* Η σχολική βάση είναι ευρεία αλλά όχι αντίγραφο κάθε επίσημου προγράμματος χώρας.
* Δεν αντικαθιστά δάσκαλο, βιβλίο, γιατρό, δικηγόρο, οικονομικό σύμβουλο ή υπηρεσία έκτακτης ανάγκης.
* Τα hardware thresholds είναι συντηρητικές εκτιμήσεις.
* Η δημόσια web learning μπορεί να αποτύχει λόγω σύνδεσης, robots, αλλαγών ιστοσελίδων ή provider limits.
* Η web γνώση μπορεί να είναι παλιά, ελλιπής ή λανθασμένη.
* Έλεγχε σημαντικά στοιχεία και υπολογισμούς.

</details>

<a id="συντελεστές"></a>

<details>
<summary><strong>Συντελεστές</strong></summary>

* **Δημιουργός:** dedsec1121fk
* **Project:** Pocket AI / DedSec Project
* **Platform:** Android + Termux
* **Γλώσσες:** Αγγλικά και Ελληνικά
* **Local model runtime:** `llama.cpp`
* **Compact language-model family:** SmolLM2
* **GitHub:** [dedsec1121fk/Pocket-AI](https://github.com/dedsec1121fk/Pocket-AI)
* **Website:** [ded-sec.space](https://ded-sec.space)
* **Sponsors:** [GitHub Sponsors](https://github.com/sponsors/dedsec1121fk)

</details>

<a id="αποποίηση-ευθύνης"></a>

<details>
<summary><strong>Αποποίηση Ευθύνης</strong></summary>

Το Pocket AI παρέχεται για εκπαιδευτική, προσωπική και πειραματική χρήση **ΩΣ ΕΧΕΙ**, χωρίς εγγύηση ακρίβειας, διαθεσιμότητας ή καταλληλότητας. Ο δημιουργός και οι contributors δεν ευθύνονται για ζημιές, απώλεια δεδομένων, λάθος αποφάσεις, υπερθέρμανση, κατανάλωση μπαταρίας, περιορισμούς λογαριασμών ή άλλες συνέπειες χρήσης ή κατάχρησης.

Χρησιμοποίησε το web learning μόνο για νόμιμη δημόσια έρευνα. Σεβάσου όρους ιστοσελίδων, copyright, ιδιωτικότητα, robots rules και νομοθεσία. Μη χρησιμοποιείς search operators για credentials, ιδιωτικά συστήματα, εκτεθειμένες συσκευές ή δεδομένα χωρίς άδεια.

</details>
