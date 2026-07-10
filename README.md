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


## Maximum-smartness architecture

Pocket AI now uses an evidence-first reasoning stack before any language-model call. The advanced reasoning module decomposes requests, extracts comparison entities and constraints, ranks sources by reliability and coverage, runs exact local tools for arithmetic, equations, statistics, conversions, and exact text counting, constructs a compact reasoning blueprint, audits generated answers, and repairs weak output with grounded synthesis. Qwen3 runs in non-thinking mode for routine questions and guarded thinking mode only for difficult tasks when live RAM, CPU, temperature, and the shared deadline permit it. The 135M models remain emergency generators; retrieval and deterministic tools carry most factual and exact work on low-end phones.

## Table of Contents

* [Main Features](#main-features)
* [Universal Knowledge And Natural Conversation](#universal-knowledge-and-natural-conversation)
* [Maximum Smartness Under Two Minutes](#maximum-smartness-under-two-minutes)
* [Hardware Combination Matrix](#hardware-combination-matrix)
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
* **Complete school foundation:** 758 searchable concepts and 3,893 grade-adapted lessons across grades 1–12, shared by every model profile.
* **Maximum retrieval foundation:** 12,775 curated bilingual records, 117,659 WordNet concepts, and 68,342 offline encyclopedia passages are available to every model route.
* **Continuous runtime matrix:** tunes model, classifier, hybrid mode, context, batch, tokens, and threads from live phone conditions.
* **No-key public research:** can learn from safe public search results, Wikipedia, and readable public pages.
* **Safe operator research:** supports public `site:`, `filetype:`, `intitle:`, `inurl:`, `before:`, `after:`, exact phrases, and excluded words.
* **Local file learning:** indexes English and Greek text documents and folders.
* **No TensorFlow, PyTorch, or NumPy required:** the main assistant uses Python’s standard library and bundled files.

</details>


<a id="universal-knowledge-and-natural-conversation"></a>

<details open>
<summary><strong>Universal Knowledge And Natural Conversation</strong></summary>

Pocket AI now gives **every model path** the same shared bilingual foundation before a transformer is used. This prevents weak phones from losing basic capabilities simply because they cannot run the Quality model.

* **12,775 indexed bilingual knowledge records** covering school subjects, countries and capitals, chemistry, physical constants, programming APIs, arithmetic tables, fractions, number theory, everyday concepts, and specialist guidance.
* **117,659 WordNet concepts** with 206,978 English lemma records, plus 17,891 Greek-linked concepts and 23,853 Greek lemma records.
* **45,591 offline encyclopedia articles** split into 68,342 searchable passages and five low-RAM FTS5 shards.
* **72 grade-and-subject curriculum summaries** covering grades 1–12 across mathematics, science, language, history, geography, and computing.
* **Natural conversation** for greetings, feelings, confusion, capabilities, thanks, corrections, and ordinary conversational turns.
* **Context-aware follow-ups:** “simpler,” “go deeper,” “another example,” “use an analogy,” and “quiz me” continue the actual topic instead of starting over.
* **Understanding recovery:** when the learner says they are confused, Pocket AI changes the explanation method rather than repeating the same wording.
* **Follow-up understanding** for messages such as `tell me more`, `why`, `continue`, `πες μου περισσότερα`, and `γιατί`.
* **Shared routing order:** school tools → universal knowledge → learned local documents → specialists → classifier → optional GGUF.
* **Fast exact-answer path:** known facts and exact mathematics can be returned directly without starting a transformer.
* **Cross-model knowledge bridge:** only the most relevant facts are injected into the selected model, keeping prompts compact and responses fast.
* **Low-RAM design:** the large knowledge pack stays in a read-only SQLite FTS index instead of being loaded fully into Python memory.
* **Safe response cache:** high-confidence static generated answers can be reused, while current information such as weather, prices, news, and time is never treated as permanent.
* **Human-style output:** the selected persona changes tone while facts, calculations, commands, and code remain protected from unnecessary rewriting.
* **English and Greek consistency:** the same concept can be asked naturally in either supported language.
* **Offline reliability:** common definitions and school foundations work even when `llama.cpp` is not installed.

Examples:

* `What is a prime number?`
* `What is the capital of Japan?`
* `Explain the circulatory system.`
* `What does RAM do?`
* `Grade 8 science topics.`
* `Ποια είναι η πρωτεύουσα της Γαλλίας;`
* `Τι είναι το νευρικό σύστημα;`
* `Εξήγησε την πιθανότητα.`

Use `/knowledge` or `/γνώσεις` to show the active shared knowledge foundation.

</details>

<a id="maximum-smartness-under-two-minutes"></a>

<details open>
<summary><strong>Maximum Smartness Under Two Minutes</strong></summary>

The smallest bundled Q2_K model is now used as an **evidence synthesizer**. Pocket AI searches its local databases first, sends only the strongest passages into the active context window, and then asks the model to compose and verify the answer. A 135M-parameter model still cannot equal a cloud frontier model, so this edition also supports stronger Qwen tiers without sacrificing the bundled low-end fallback.

* **Retrieval-first prompts:** curated facts, encyclopedia passages, and lexical evidence are ranked separately for every question.
* **Cross-language evidence retrieval:** Greek questions are converted into compact English search variants while the final answer remains Greek.
* **Entity-balanced comparisons:** A-vs-B questions retrieve evidence for both sides instead of letting words such as “compare” dominate the ranking.
* **Verified expert fallbacks:** common networking, hardware, web-security, cryptography, and science questions have deterministic bilingual answers when generation is unreliable.
* **Broad offline knowledge:** 45,591 encyclopedia articles, 117,659 lexical concepts, the 12,775-record bilingual foundation, school curricula, user documents, memories, and learned Q&A.
* **More context on small phones:** Q2_K receives enlarged but guarded context windows, with automatic reductions when RAM or temperature becomes unsafe.
* **Deliberate reasoning:** prompts require the model to plan silently, check logic and mathematics, distinguish facts from inference, and avoid fabricated sources, dates, commands, or security claims.
* **Direct factual path:** exact static topics can be answered from indexed evidence without spending transformer time.
* **One global time plan:** local generation and optional verification share a maximum 112-second inference budget; low-end profiles use one strong pass instead of wasting time on repeated drafts.
* **Sub-60 MB bundled files:** both bundled 135M GGUF models and every knowledge shard remain below the per-file limit, although the complete project is intentionally much larger.


### Stronger optional intelligence tiers

* **Qwen3 0.6B Smart:** the recommended reasoning upgrade for capable 4 GB+ 64-bit phones. Pocket AI uses short context, one guarded pass, and non-thinking mode on entry-level hardware.
* **Qwen3 1.7B Ultra:** the strongest supported local tier, intended mainly for capable 8 GB-class phones. Pocket AI keeps context, thinking, and answer length guarded to protect the time budget.
* **Smallest-model protection:** when only the bundled 135M model is available, the same query planner, evidence reranker, exact-answer tools, bilingual retrieval, answer validator, and safe fallback remain active.

Install either optional model directly from its official repository with resumable download and SHA-256 verification:

```bash
bash "Other Files/install_smart_models.sh" smart
# Stronger but much larger:
bash "Other Files/install_smart_models.sh" ultra
```

Then use `/llm-model smart`, `/llm-model ultra`, or leave `/hybrid auto` enabled.

The two-minute target covers Pocket AI's local inference plan after startup. First-run GGUF reconstruction, very slow storage, Android scheduling, severe thermal throttling, or an external `llama.cpp` build can add overhead, so no device-independent wall-clock guarantee is possible.

See `Other Files/Documentation/MAX_KNOWLEDGE_ARCHITECTURE.md` for the complete routing and timing design.

</details>

<a id="hardware-combination-matrix"></a>

<details open>
<summary><strong>Hardware Combination Matrix</strong></summary>

Pocket AI does not assume that every phone advertised with the same RAM performs equally. It continuously combines:

* total RAM
* currently available RAM
* processor family and measured CPU score
* 32-bit or 64-bit Termux userspace
* logical CPU cores
* free application storage
* phone and battery temperature
* battery level and charging state
* selected 135M, Qwen3 0.6B, or Qwen3 1.7B model tier

Representative automatic combinations:

| Phone state | Selected stack | Runtime behavior |
| :-- | :-- | :-- |
| **512 MB–1 GB or 32-bit** | Internal engine + Micro/Lite | One thread, no GGUF, smallest memory footprint |
| **1.5–2 GB, slow CPU** | Q2_K Fast + Balanced | Eco context and batch, short answers |
| **2 GB, capable 64-bit CPU** | Q2_K Fast + Balanced | Entry profile with up to two useful threads |
| **3 GB, entry CPU** | Q2_K Fast + Standard | Smart routing with conservative context |
| **3 GB, capable CPU and free RAM** | Q4_1 Quality + Standard | Quality single pass when safe |
| **4 GB, entry/mid CPU** | Q4_1 Quality + Max | Adaptive quality routing |
| **6 GB, strong CPU** | Q2_K draft → Q4_1 verification | Sequential Cascade, never simultaneous |
| **8 GB+, flagship-class CPU** | Independent Q2_K and Q4_1 answers | Sequential Consensus selection |

Live safeguards can immediately reduce threads, context, batch, micro-batch, or output length when Android consumes RAM or the phone becomes hot. Unknown processors are benchmarked instead of being rejected because their name is absent from a list.

The complete matrix is stored in `Other Files/Documentation/HARDWARE_COMBINATIONS.md`.

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
| **Storage** | Enough for Python and the repository | At least 1.5 GB free for knowledge indexes, reconstructed models, build files, and saves |
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

The two 135M GGUF weights are bundled as verified **48 MiB parts** under `Models/GGUF Parts/`, so no packaged model file exceeds 60 MB. The installer reconstructs them under `Other Files/Saved Data/GGUF Models/`, verifies their SHA-256 hashes, and builds the phone-compatible `llama.cpp` runner. Optional Qwen weights are downloaded only when you explicitly run `install_smart_models.sh`.

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

The current school database contains **758 core concepts** and **3,893 grade-adapted lesson records**. Each detailed lesson can provide a learning goal, prerequisites, a core explanation, a teaching strategy, vocabulary, a worked or guided example, a common misconception, practice, a mastery check, related topics, and local evidence. Ask for a grade and say **“in detail”** when you want the full lesson.

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
* **Computing and digital systems**
  * hardware, software, operating systems, CPU, memory, files, and storage
  * algorithms, variables, conditions, loops, functions, data structures, testing, and debugging
  * networks, OSI/TCP-IP layers, TCP/UDP, IP, DNS, HTTP/HTTPS, databases, and SQL
  * cybersecurity, encryption, hashing, authentication, malware, phishing, and web safety
  * artificial intelligence, machine learning, neural networks, robotics, software engineering, and digital ethics
* **Health, life skills, arts, and economics**
  * physical and mental wellbeing, first aid, relationships, study habits, time management, budgeting, and career skills
  * drawing, painting, sculpture, photography, design, music, theatre, dance, film, and creative process
  * scarcity, opportunity cost, supply and demand, markets, inflation, banking, taxation, trade, and public policy

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
Explain photosynthesis in detail for grade 7.
Teach me the French Revolution in detail for grade 10.
Explain network layers for grade 11 with an example.
```

Greek examples:

```text
/school 5 μαθηματικά
/school 9 επιστήμες
/school 12 πληροφορική
Εξήγησε αναλυτικά τη φωτοσύνθεση για τάξη 7.
Δίδαξέ μου τη Γαλλική Επανάσταση αναλυτικά για τάξη 10.
Εξήγησε τα επίπεδα δικτύου για τάξη 11 με παράδειγμα.
```

> No finite offline package can contain every sentence from every country’s textbooks. This build instead provides a broad, detailed grade 1–12 concept map with structured lessons and local evidence, while clearly avoiding the claim that it is an exact copy of every national curriculum or examination board.

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
  * used as the stronger bundled fallback

### Optional Qwen GGUF models

* **Qwen3-0.6B Q8_0 Smart** — recommended reasoning upgrade for capable 4 GB+ phones.
* **Qwen3-1.7B Q8_0 Ultra** — strongest supported tier for capable 8 GB-class phones.
* Both are installed with `Other Files/install_smart_models.sh`, verified by exact SHA-256, and loaded one at a time.

### Split-model packaging

Each GGUF is distributed as two ordered binary parts. Every part is at most 48 MiB, safely below the requested 60 MB ceiling. Pocket AI automatically reconstructs only the selected model when inference needs it, verifies every part and the final model hash, and reuses the verified runtime copy on later launches.

* Q2_K: 50,331,648 bytes + 37,870,144 bytes
* Q4_1: 50,331,648 bytes + 48,030,784 bytes
* Runtime cache: `Other Files/Saved Data/GGUF Models/`
* Package manifest: `Models/GGUF Parts/split_models_manifest.json`

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
* **Consensus:** compares a compact draft with a stronger verification answer sequentially
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
│   ├── GGUF Parts/ (all parts below 60 MB)
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
    ├── install_models.sh
    └── install_smart_models.sh
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

Bundled model parts remain under `Models/GGUF Parts/`. Reconstructed runtime models are stored under `Other Files/Saved Data/GGUF Models/` and can be deleted safely; Pocket AI recreates them from the verified parts when needed.

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
* `/knowledge`
* `/matrix`
* `/stats`
* `/system`
* `/llm-status`
* `/llm off|fallback|always`
* `/llm-model fast|quality|smart|ultra`
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
* [Καθολική Γνώση και Φυσική Συζήτηση](#καθολική-γνώση-και-φυσική-συζήτηση)
* [Μέγιστη Ευφυΐα Κάτω από Δύο Λεπτά](#μέγιστη-ευφυΐα-κάτω-από-δύο-λεπτά)
* [Πίνακας Συνδυασμών Hardware](#πίνακας-συνδυασμών-hardware)
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
* **Μέγιστη βάση ανάκτησης:** 12.775 επιμελημένες δίγλωσσες εγγραφές, 117.659 έννοιες WordNet και 68.342 offline εγκυκλοπαιδικά αποσπάσματα για κάθε διαδρομή μοντέλου.
* **Συνεχής πίνακας runtime:** ρυθμίζει μοντέλο, classifier, hybrid mode, context, batch, tokens και threads από τη ζωντανή κατάσταση του κινητού.
* **Δημόσια έρευνα χωρίς API key:** μάθηση από ασφαλή δημόσια αποτελέσματα, Wikipedia και αναγνώσιμες δημόσιες σελίδες.
* **Ασφαλείς τελεστές αναζήτησης:** `site:`, `filetype:`, `intitle:`, `inurl:`, `before:`, `after:`, ακριβείς φράσεις και εξαιρούμενες λέξεις.
* **Μάθηση από τοπικά αρχεία:** ευρετηρίαση αγγλικών και ελληνικών εγγράφων και φακέλων.
* **Χωρίς απαίτηση TensorFlow, PyTorch ή NumPy:** ο βασικός βοηθός χρησιμοποιεί standard library και ενσωματωμένα αρχεία.

</details>


<a id="καθολική-γνώση-και-φυσική-συζήτηση"></a>

<details open>
<summary><strong>Καθολική Γνώση και Φυσική Συζήτηση</strong></summary>

Το Pocket AI δίνει πλέον **σε κάθε διαδρομή μοντέλου** την ίδια κοινή δίγλωσση βάση πριν χρησιμοποιηθεί transformer. Έτσι, ένα αδύναμο κινητό δεν χάνει βασικές δυνατότητες επειδή δεν μπορεί να τρέξει το Quality μοντέλο.

* **12.775 ευρετηριασμένες εγγραφές γνώσης** για καθημερινές έννοιες, μαθηματικά, επιστήμες, πληροφορική, γλώσσα, γεωγραφία, ιστορία, αγωγή του πολίτη, οικονομία, υγεία και δεξιότητες μελέτης.
* **117.659 έννοιες WordNet** με 206.978 αγγλικά λήμματα, 17.891 έννοιες συνδεδεμένες με Ελληνικά και 23.853 ελληνικά λήμματα.
* **45.591 offline εγκυκλοπαιδικά άρθρα** σε 68.342 αναζητήσιμα αποσπάσματα και πέντε low-RAM shards FTS5.
* **72 περιλήψεις τάξης και μαθήματος** για τάξεις 1–12 σε μαθηματικά, επιστήμες, γλώσσα, ιστορία, γεωγραφία και πληροφορική.
* **Φυσική καθημερινή συζήτηση** για χαιρετισμούς, ευχαριστίες, ονόματα, συγγνώμες και απλές συνομιλίες.
* **Κατανόηση συνέχειας** για φράσεις όπως `πες μου περισσότερα`, `γιατί`, `συνέχισε`, `tell me more` και `continue`.
* **Κοινή σειρά δρομολόγησης:** σχολικά εργαλεία → καθολική γνώση → τοπικά έγγραφα → specialists → classifier → προαιρετικό GGUF.
* **Γρήγορη διαδρομή ακριβούς απάντησης:** γνωστά γεγονότα και ακριβείς μαθηματικοί υπολογισμοί απαντώνται χωρίς εκκίνηση transformer.
* **Γέφυρα γνώσης μεταξύ μοντέλων:** μόνο τα πιο σχετικά στοιχεία περνούν στο επιλεγμένο μοντέλο, ώστε το prompt να μένει μικρό και γρήγορο.
* **Σχεδιασμός χαμηλής RAM:** η μεγάλη βάση παραμένει σε read-only SQLite FTS index και δεν φορτώνεται ολόκληρη στη μνήμη Python.
* **Ασφαλής cache απαντήσεων:** στατικές απαντήσεις υψηλής βεβαιότητας επαναχρησιμοποιούνται, αλλά καιρός, τιμές, ειδήσεις και ώρα δεν αποθηκεύονται ως μόνιμα γεγονότα.
* **Ανθρώπινο ύφος:** η persona αλλάζει τον τόνο, ενώ γεγονότα, υπολογισμοί, εντολές και κώδικας προστατεύονται από περιττή επανεγγραφή.
* **Συνέπεια Αγγλικών και Ελληνικών:** η ίδια έννοια μπορεί να ζητηθεί φυσικά και στις δύο γλώσσες.
* **Offline αξιοπιστία:** βασικοί ορισμοί και σχολικές γνώσεις λειτουργούν ακόμη και χωρίς εγκατεστημένο `llama.cpp`.

Παραδείγματα:

* `Τι είναι πρώτος αριθμός;`
* `Ποια είναι η πρωτεύουσα της Γαλλίας;`
* `Εξήγησε το κυκλοφορικό σύστημα.`
* `Τι κάνει η RAM;`
* `Θέματα επιστήμης τάξης 8.`
* `What is a prime number?`
* `Explain probability.`

Χρησιμοποίησε `/knowledge` ή `/γνώσεις` για να δεις την ενεργή κοινή βάση γνώσης.

</details>

<a id="μέγιστη-ευφυΐα-κάτω-από-δύο-λεπτά"></a>

<details open>
<summary><strong>Μέγιστη Ευφυΐα Κάτω από Δύο Λεπτά</strong></summary>

Το μικρότερο μοντέλο Q2_K λειτουργεί πλέον ως **συνθέτης τεκμηρίων**. Το Pocket AI αναζητά πρώτα στις τοπικές βάσεις, βάζει μόνο τα πιο σχετικά αποσπάσματα στο context και μετά ζητά από το μοντέλο να συνθέσει και να ελέγξει την απάντηση. Ένα μοντέλο 135M παραμέτρων δεν μπορεί να γίνει ισάξιο με cloud frontier μοντέλο, γι’ αυτό υποστηρίζονται και ισχυρότερα προαιρετικά Qwen tiers.

* **Retrieval-first prompts:** ξεχωριστή κατάταξη επιμελημένων γεγονότων, εγκυκλοπαιδικών αποσπασμάτων και λεξιλογικών στοιχείων.
* **Ευρεία offline γνώση:** 45.591 άρθρα, 117.659 λεξιλογικές έννοιες, 12.775 δίγλωσσες εγγραφές, σχολική ύλη, έγγραφα χρήστη, μνήμες και διδαγμένα Q&A.
* **Μεγαλύτερο context με προστασία:** αυξάνεται η χρήσιμη πληροφορία για το Q2_K, αλλά μειώνεται αυτόματα όταν η RAM ή η θερμοκρασία δεν είναι ασφαλής.
* **Προσεκτική συλλογιστική:** έλεγχος λογικής και μαθηματικών, διαχωρισμός γεγονότων από συμπεράσματα και απαγόρευση επινοημένων πηγών, ημερομηνιών, εντολών ή ισχυρισμών ασφαλείας.
* **Άμεση διαδρομή γεγονότων:** ακριβή στατικά θέματα μπορούν να απαντηθούν από το index χωρίς να καταναλωθεί χρόνος transformer.
* **Ενιαίο χρονικό πλάνο:** η δημιουργία και ο προαιρετικός έλεγχος μοιράζονται έως 112 δευτερόλεπτα inference. Τα αδύναμα κινητά χρησιμοποιούν μία ισχυρή διέλευση.
* **Αρχεία κάτω από 60 MB:** μοντέλα και shards μένουν κάτω από το όριο ανά αρχείο, παρότι το συνολικό project είναι σκόπιμα μεγαλύτερο.


### Ισχυρότερα προαιρετικά tiers

* **Qwen3 0.6B Smart:** προτεινόμενη αναβάθμιση συλλογισμού για ικανά 64-bit κινητά με 4 GB+ RAM.
* **Qwen3 1.7B Ultra:** το ισχυρότερο υποστηριζόμενο τοπικό tier, κυρίως για ικανά κινητά κατηγορίας 8 GB RAM.
* **Προστασία μικρού μοντέλου:** ακόμη και με μόνο το 135M παραμένουν ενεργά planner, reranking, exact tools, δίγλωσσο retrieval, validation και ασφαλές fallback.

```bash
bash "Other Files/install_smart_models.sh" smart
# Ισχυρότερο αλλά πολύ μεγαλύτερο:
bash "Other Files/install_smart_models.sh" ultra
```

Μετά χρησιμοποίησε `/μοντέλο smart`, `/μοντέλο ultra` ή άφησε ενεργό το `/υβριδικό auto`.

Ο στόχος των δύο λεπτών αφορά το τοπικό πλάνο inference μετά την εκκίνηση. Η πρώτη ανακατασκευή GGUF, πολύ αργός αποθηκευτικός χώρος, το Android, έντονο thermal throttling ή εξωτερικό build του `llama.cpp` μπορούν να προσθέσουν χρόνο.

</details>

<a id="πίνακας-συνδυασμών-hardware"></a>

<details open>
<summary><strong>Πίνακας Συνδυασμών Hardware</strong></summary>

Το Pocket AI δεν θεωρεί ότι όλα τα κινητά με την ίδια διαφημιζόμενη RAM έχουν ίδιες επιδόσεις. Συνδυάζει συνεχώς:

* συνολική RAM
* πραγματικά διαθέσιμη RAM
* οικογένεια επεξεργαστή και μετρημένο CPU score
* 32-bit ή 64-bit περιβάλλον Termux
* λογικούς πυρήνες CPU
* ελεύθερο χώρο εφαρμογής
* θερμοκρασία κινητού και μπαταρίας
* επίπεδο μπαταρίας και κατάσταση φόρτισης
* επιλεγμένη κβαντοποίηση Q2_K ή Q4_1

Ενδεικτικοί αυτόματοι συνδυασμοί:

| Κατάσταση κινητού | Επιλεγμένο stack | Συμπεριφορά runtime |
| :-- | :-- | :-- |
| **512 MB–1 GB ή 32-bit** | Internal engine + Micro/Lite | Ένα thread, χωρίς GGUF, ελάχιστη μνήμη |
| **1.5–2 GB, αργός CPU** | Q2_K Fast + Balanced | Eco context και batch, σύντομες απαντήσεις |
| **2 GB, ικανός 64-bit CPU** | Q2_K Fast + Balanced | Entry profile με έως δύο χρήσιμα threads |
| **3 GB, entry CPU** | Q2_K Fast + Standard | Smart routing με συντηρητικό context |
| **3 GB, ικανός CPU και ελεύθερη RAM** | Q4_1 Quality + Standard | Ποιοτικό μονό πέρασμα όταν είναι ασφαλές |
| **4 GB, entry/mid CPU** | Q4_1 Quality + Max | Adaptive ποιοτική δρομολόγηση |
| **6 GB, ισχυρός CPU** | Q2_K draft → Q4_1 verification | Διαδοχικό Cascade, ποτέ ταυτόχρονα |
| **8 GB+, flagship CPU** | Ανεξάρτητες Q2_K και Q4_1 απαντήσεις | Διαδοχική επιλογή Consensus |

Οι ζωντανές δικλείδες μπορούν να μειώσουν αμέσως threads, context, batch, micro-batch ή μήκος απάντησης όταν το Android καταναλώνει RAM ή το κινητό ζεσταίνεται. Οι άγνωστοι επεξεργαστές μετρώνται με benchmark αντί να απορρίπτονται επειδή λείπει το όνομά τους από λίστα.

Ο πλήρης πίνακας βρίσκεται στο `Other Files/Documentation/HARDWARE_COMBINATIONS.md`.

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
| **Αποθήκευση** | Αρκετή για Python και repository | Τουλάχιστον 1,5 GB ελεύθερα για indexes γνώσης, ανακατασκευασμένα μοντέλα, build και saves |
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

Τα δύο 135M GGUF περιλαμβάνονται ως επαληθευμένα κομμάτια **48 MiB** στο `Models/GGUF Parts/`. Ο installer τα ανακατασκευάζει στο `Other Files/Saved Data/GGUF Models/`, επαληθεύει τα SHA-256 και δημιουργεί τον συμβατό `llama.cpp` runner. Τα προαιρετικά Qwen weights κατεβαίνουν μόνο όταν εκτελέσεις ρητά το `install_smart_models.sh`.

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

Η τρέχουσα σχολική βάση περιέχει **758 βασικές έννοιες** και **3.893 προσαρμοσμένα μαθήματα τάξης**. Κάθε αναλυτικό μάθημα μπορεί να δώσει μαθησιακό στόχο, προαπαιτούμενα, βασική εξήγηση, στρατηγική διδασκαλίας, λεξιλόγιο, καθοδηγούμενο παράδειγμα, συνηθισμένη παρανόηση, εξάσκηση, έλεγχο κατάκτησης, σχετικά θέματα και τοπικά τεκμήρια. Γράψε τάξη και **«αναλυτικά»** για πλήρες μάθημα.

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
  * ισχυρότερο ενσωματωμένο fallback

### Προαιρετικά Qwen GGUF μοντέλα

* **Qwen3-0.6B Q8_0 Smart** — προτεινόμενη αναβάθμιση συλλογισμού για ικανά κινητά 4 GB+.
* **Qwen3-1.7B Q8_0 Ultra** — ισχυρότερο tier για ικανά κινητά κατηγορίας 8 GB.
* Εγκαθίστανται με `Other Files/install_smart_models.sh`, επαληθεύονται με SHA-256 και φορτώνεται μόνο ένα κάθε φορά.

### Διανομή μοντέλων σε κομμάτια

Κάθε GGUF διανέμεται σε δύο ταξινομημένα binary parts. Κάθε part είναι έως 48 MiB, κάτω από το όριο των 60 MB. Το Pocket AI ανακατασκευάζει αυτόματα το επιλεγμένο μοντέλο όταν χρειάζεται inference, επαληθεύει κάθε part και το τελικό hash και επαναχρησιμοποιεί το verified runtime copy στις επόμενες εκκινήσεις.

* Q2_K: 50.331.648 bytes + 37.870.144 bytes
* Q4_1: 50.331.648 bytes + 48.030.784 bytes
* Runtime cache: `Other Files/Saved Data/GGUF Models/`
* Package manifest: `Models/GGUF Parts/split_models_manifest.json`

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
│   ├── GGUF Parts/ (όλα τα parts κάτω από 60 MB)
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
    ├── install_models.sh
    └── install_smart_models.sh
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
* ανακατασκευασμένα runtime GGUF στο `Other Files/Saved Data/GGUF Models/`

Τα packaged model parts παραμένουν στο `Models/GGUF Parts/`. Τα runtime GGUF μπορούν να διαγραφούν με ασφάλεια και θα δημιουργηθούν ξανά από τα verified parts όταν χρειαστούν.

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
* `/γνώσεις`
* `/matrix`
* `/stats`
* `/system`
* `/llm-status`
* `/llm off|fallback|always`
* `/μοντέλο fast|quality|smart|ultra`
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
* Καμία πεπερασμένη offline βάση δεν περιέχει κάθε πρόταση από κάθε σχολικό βιβλίο. Η παρούσα βάση καλύπτει 758 έννοιες και 3.893 αναλυτικά μαθήματα τάξης, αλλά δεν ισχυρίζεται ότι αντιγράφει κάθε εθνικό πρόγραμμα ή εξεταστικό φορέα.
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
