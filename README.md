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

> **Pocket AI 16.0 model policy:** normal local inference begins at **0.6B**, then scales through **0.8B, 1.5B, 1.7B, 2B, and 3.09B**. The 135M models are emergency-only. Adjacent hybrids run one model at a time; their parameters are not added. Use `--extended` to download the full 0.6B–3.09B ladder.


> **Για να μεταβείτε στην πλήρη Ελληνική έκδοση, συνεχίστε [πατώντας εδώ](#greek-readme).**

**Pocket AI** is a bilingual local assistant for **English and Greek** that runs in **Termux without root**. It combines compact neural classifiers, local GGUF language models, persistent retrieval memory, subject specialists, deterministic school tools, and hardware-aware hybrid routing.

<details>
<summary><strong>Extended 3B Hybrid Intelligence: 0.6B to 3.09B</strong></summary>

Pocket AI 16.0 begins normal local inference at **Qwen3 0.6B**, not 135M. It adds real intermediate tiers and selects the strongest safe installed model from live phone conditions.

| Tier key | Model | Parameters | Purpose |
|---|---|---:|---|
| Emergency Fast | SmolLM2 Q2_K | 134.52M | critical low-memory fallback |
| Emergency Quality | SmolLM2 Q4_1 | 134.52M | higher-precision emergency fallback |
| Fast | Qwen3 Q8_0 | 0.6B | normal minimum |
| Quality | Qwen3.5 Q4_0 | 0.8B | compact quality bridge |
| Smart | Qwen2.5 Instruct Q4_K_M | about 1.5B | advanced compact instruction tier |
| Ultra | Qwen3 Q4_K_M | 1.7B | strongest compact tier |
| Pro / Max | Qwen3 Q4_K_M | 4B / 8B | optional high-end tiers |

Adjacent hybrids run sequentially: `0.6B→0.8B`, `0.8B→1.5B`, `1.5B→1.7B`, `1.7B→2B`, and `2B→3.09B`. The first model is unloaded before the stronger model starts. The parameters are **not added**; for example, 0.6B→0.8B is not a 1.4B model.

The shared foundation still contains **12,842 bilingual knowledge entries**, **78,509 aliases**, and **771 school topics / 3,994 grade-specific lessons**.

**Honest limit:** retrieval, exact tools, verification, and sequential orchestration improve small local models, but do not literally transform them into GPT-3.5.

### Ελληνικά

Το Pocket AI 16.0 ξεκινά κανονικά από πραγματικό μοντέλο **0.6B** και προσθέτει πραγματικά tiers 0.8B, 1.5B, 1.7B, 2B και 3.09B. Τα δύο 135M παραμένουν μόνο ως emergency fallback. Τα υβριδικά routes είναι διαδοχικά και οι παράμετροι δεν αθροίζονται.

</details>

<details>
<summary><strong>MaxSafe Phone-Limit Intelligence</strong></summary>

Pocket AI 16.0 uses the strongest installed model that fits the phone <strong>right now</strong>, not merely the largest model found on disk. It combines live RAM, processor score, CPU-core count, battery state, available storage, temperature sensors, recent temperature rise, task difficulty, and the remaining answer deadline.

● <strong>Cool-device burst:</strong> raises useful threads and batch size for short work while leaving at least one logical core available to Android and Termux.

● <strong>Sustained protection:</strong> reduces threads, context, batch, micro-batch, and output length as the phone becomes warm or memory pressure rises.

● <strong>Emergency stop:</strong> stops a model pass on emergency heat, critical rapid temperature rise, critical free-RAM pressure, or the shared 112-second deadline. A coherent partial answer or retrieval/tool fallback is preserved where possible.

● <strong>Sequential fusion:</strong> for difficult questions on capable phones, a smaller model acts as analyst. It is unloaded before the strongest safe model synthesizes the final answer from the question, evidence, conversation context, and analyst notes. Two GGUF models are never kept loaded together.

● <strong>Adaptive compute learning:</strong> records each model's real output speed, temperature rise, abort rate, context, batch, and thread count on this phone. Future answers use that history to spend more of the 112-second budget when the device stays cool and to back off earlier when the same model heats the device quickly.

● <strong>Guarded final critic:</strong> very difficult mathematics, coding, comparison, and causal questions can receive one short final verification pass on Qwen3 when the phone remains cool, free RAM is sufficient, and at least 16 seconds remain. The verifier is skipped immediately if any safety condition tightens.

● <strong>Automatic best match:</strong> `bash "Other Files/install_models.sh" --best` selects the strongest practical Qwen3 tier from the phone's RAM, architecture, and free storage. Inside Pocket AI, keep `/llm-model auto` and `/hybrid auto` enabled.

| Approximate phone class | Strongest conservative starting tier |
|---|---|
| Under 3 GB or severe live pressure | 135M emergency fallback |
| Capable 3–4 GB 64-bit phone | Qwen3 0.6B Q8_0 Fast |
| Strong 4 GB / typical 6 GB phone | Qwen3.5 0.8B Q4_0 Quality |
| Capable 5–6 GB phone | Qwen2.5 1.5B Q4_K_M Smart |
| Capable 6–8 GB phone | Qwen3 1.7B Q4_K_M Ultra |
| Strong 8–12 GB phone | Qwen3 4B Q4_K_M Pro |
| 12 GB+ with sufficient live headroom | Qwen3 8B Q4_K_M Max |

These are conservative starting bands. Live free RAM and thermal state can cause Pocket AI to select a smaller tier. Pocket AI never disables Android thermal protection, and no software can guarantee that a phone will never become warm.

### Ελληνικά

Το Pocket AI 16.0 επιλέγει το ισχυρότερο εγκατεστημένο μοντέλο που χωράει με ασφάλεια στην πραγματική κατάσταση του κινητού. Παρακολουθεί RAM, CPU, μπαταρία, αισθητήρες θερμοκρασίας και την άνοδο θερμοκρασίας κατά την απάντηση. Η λειτουργία `fusion` χρησιμοποιεί δύο μοντέλα <strong>διαδοχικά</strong>, ποτέ ταυτόχρονα: πρώτα έναν μικρό αναλυτή και μετά το ισχυρότερο ασφαλές μοντέλο για την τελική σύνθεση.
 Το Pocket AI αποθηκεύει μόνο τοπικά μετρήσεις απόδοσης ανά μοντέλο και μαθαίνει πόσο γρήγορα και πόσο θερμά λειτουργεί το συγκεκριμένο κινητό. Σε δύσκολες ερωτήσεις μπορεί να εκτελέσει έναν σύντομο τελικό έλεγχο μόνο όταν η θερμοκρασία, η RAM και ο χρόνος παραμένουν ασφαλή.

</details>

<details>
<summary><strong>Rapid Web Learning and Shared Model Intelligence</strong></summary>

Pocket AI 16.0 makes internet learning faster without pretending to retrain GGUF weights on the phone. Search providers run in parallel, readable public pages are fetched concurrently, repeated searches use a bounded cache, and trusted evidence is inserted into SQLite in one transaction instead of one transaction per paragraph.

● <strong>Safe automatic learning:</strong> `/learn safe` stores trusted evidence that was actually used in an answer.

● <strong>Fast learning:</strong> `/learn fast` reads more trusted pages in parallel while keeping the same public-host, robots.txt, file-type, size, and timeout restrictions.

● <strong>Shared lessons:</strong> high-confidence answers from stronger installed models are compressed into verified local lessons that every model can retrieve later. This lets Qwen teach the 135M emergency models without unsafe on-device fine-tuning.

● <strong>Freshness protection:</strong> time-sensitive answers are searched again and are not treated as permanent timeless lessons.

● <strong>Per-model instruction packs:</strong> tiny models rewrite a grounded draft instead of freely inventing facts; stronger models receive deeper planning, conflict-resolution, calculation, code, and completeness checks.

Use `/learn-status` to see learned sources, chunks, shared lessons, and retrieval uses.

This can make responses substantially more capable and consistent, but a 135M model cannot become genuinely equivalent to a much larger cloud model. The main gains come from retrieval, exact tools, stronger optional Qwen models, sequential fusion, and shared verified lessons.

### Ελληνικά

Το Pocket AI 16.0 εκτελεί παράλληλη αναζήτηση και ανάγνωση δημόσιων σελίδων, αποθηκεύει αξιόπιστα στοιχεία μαζικά στη SQLite και επιτρέπει στα ισχυρότερα εγκατεστημένα μοντέλα να δημιουργούν σύντομα επαληθευμένα μαθήματα για όλα τα μικρότερα μοντέλα. Η διαδικασία δεν αλλάζει ανεξέλεγκτα τα βάρη GGUF και δεν αποθηκεύει επίκαιρες πληροφορίες ως μόνιμες αλήθειες.

</details>

The normal experience is deliberately simple:

```text
Pocket AI is ready. Ask me anything, or type help for options.

You: What is an apple?
Pocket AI: An apple is an edible fruit produced by an apple tree...
```

Type **`help`** at any time to open the easy numbered menu.

<a id="english-table-of-contents"></a>


## Compact-hybrid maximum-smartness architecture

Pocket AI 16.0 starts normal GGUF inference at 0.6B and uses a conversation-aware, evidence-first reasoning stack before any language-model call. The advanced reasoning module decomposes requests, extracts comparison entities and constraints, ranks sources by reliability and coverage, runs exact local tools for arithmetic, equations, statistics, conversions, and exact text counting, constructs a compact reasoning blueprint, audits generated answers, and repairs weak output with grounded synthesis. Qwen3 runs in non-thinking mode for routine questions and guarded thinking mode only for difficult tasks when live RAM, CPU, temperature, and the shared deadline permit it. The 135M models remain emergency generators; retrieval and deterministic tools carry most factual and exact work on low-end phones.

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
* [Conversation Memory, Follow-ups, Internet Search And Learning](#conversation-memory-and-web-intelligence)
* [Google AI And API-Key Limitation](#google-ai-and-api-key-limitation)
* [Folder Structure And Save Locations](#folder-structure-and-save-locations)
* [Important Commands](#important-commands)
* [Privacy And Safety](#privacy-and-safety)
* [Limitations](#limitations)
* [Credits](#credits)
* [Disclaimer](#disclaimer)

<a id="main-features"></a>

<details>
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
* **Complete school foundation:** 771 searchable topics and 3,994 grade-adapted lessons across grades 1–12, shared by every model profile.
* **Maximum retrieval foundation:** 12,842 curated bilingual records, 117,659 WordNet concepts, and 68,342 offline encyclopedia passages are available to every model route.
* **Adaptive runtime learning:** combines live phone conditions with measured per-model speed and heat response to tune model, hybrid mode, context, batch, tokens, and threads.
* **No-key public research:** can learn from safe public search results, Wikipedia, and readable public pages.
* **Safe operator research:** supports public `site:`, `filetype:`, `intitle:`, `inurl:`, `before:`, `after:`, exact phrases, and excluded words.
* **Local file learning:** indexes English and Greek text documents and folders.
* **No TensorFlow, PyTorch, or NumPy required:** the main assistant uses Python’s standard library and bundled files.

</details>


<a id="universal-knowledge-and-natural-conversation"></a>

<details>
<summary><strong>Universal Knowledge And Natural Conversation</strong></summary>

Pocket AI now gives **every model path** the same shared bilingual foundation before a transformer is used. This prevents weak phones from losing basic capabilities simply because they cannot run the Quality model.

* **12,842 indexed bilingual knowledge records** covering school subjects, countries and capitals, chemistry, physical constants, programming APIs, arithmetic tables, fractions, number theory, everyday concepts, and specialist guidance.
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

<details>
<summary><strong>Maximum Smartness Under Two Minutes</strong></summary>

The smallest bundled Q2_K model is now used as an **evidence synthesizer**. Pocket AI searches its local databases first, sends only the strongest passages into the active context window, and then asks the model to compose and verify the answer. A 135M-parameter model still cannot equal a cloud frontier model, so this edition also supports stronger Qwen tiers without sacrificing the bundled low-end fallback.

* **Retrieval-first prompts:** curated facts, encyclopedia passages, and lexical evidence are ranked separately for every question.
* **Cross-language evidence retrieval:** Greek questions are converted into compact English search variants while the final answer remains Greek.
* **Entity-balanced comparisons:** A-vs-B questions retrieve evidence for both sides instead of letting words such as “compare” dominate the ranking.
* **Verified expert fallbacks:** common networking, hardware, web-security, cryptography, and science questions have deterministic bilingual answers when generation is unreliable.
* **Broad offline knowledge:** 45,591 encyclopedia articles, 117,659 lexical concepts, the 12,842-record bilingual foundation, school curricula, user documents, memories, and learned Q&A.
* **More context on small phones:** Q2_K receives enlarged but guarded context windows, with automatic reductions when RAM or temperature becomes unsafe.
* **Deliberate reasoning:** prompts require the model to plan silently, check logic and mathematics, distinguish facts from inference, and avoid fabricated sources, dates, commands, or security claims.
* **Direct factual path:** exact static topics can be answered from indexed evidence without spending transformer time.
* **One global time plan:** local generation and optional verification share a maximum 112-second inference budget; low-end profiles use one strong pass instead of wasting time on repeated drafts.
* **Sub-60 MB bundled files:** both bundled 135M GGUF models and every knowledge shard remain below the per-file limit, although the complete project is intentionally much larger.


### Stronger optional intelligence tiers

* **Qwen3 0.6B Fast:** a compact reasoning upgrade for capable 4 GB+ 64-bit phones. Pocket AI uses short context, one guarded pass, and non-thinking mode on entry-level hardware.
* **Qwen3 1.7B Ultra:** a stronger local tier intended mainly for capable 6–8 GB phones. Pocket AI keeps context, thinking, and answer length guarded to protect the time budget.
* **Smallest-model protection:** when only the bundled 135M model is available, the same query planner, evidence reranker, exact-answer tools, bilingual retrieval, answer validator, and safe fallback remain active.
* **Qwen3 4B Pro:** the first tier intended to approach a modern assistant experience on many ordinary knowledge and reasoning tasks; designed for strong 8 GB-class phones.
* **Qwen3 8B Max:** the strongest supported tier, intended for high-end 12 GB+ phones with substantial free RAM and storage.
* **Honest capability boundary:** the bundled 135M models cannot be made genuinely equivalent to ChatGPT 3.5 by prompting or adding facts. Pocket AI improves them with retrieval, exact tools, conversation memory, verification, and web grounding, then automatically selects a larger model when the phone can safely run one.

Install either optional model directly from its official repository with resumable download and SHA-256 verification:

```bash
bash "Other Files/install_smart_models.sh" smart
# Progressively stronger and larger:
bash "Other Files/install_smart_models.sh" ultra
bash "Other Files/install_smart_models.sh" pro
bash "Other Files/install_smart_models.sh" max
```

Then use `/llm-model smart`, `/llm-model ultra`, or leave `/hybrid auto` enabled.

The two-minute target covers Pocket AI's local inference plan after startup. First-run GGUF reconstruction, very slow storage, Android scheduling, severe thermal throttling, or an external `llama.cpp` build can add overhead, so no device-independent wall-clock guarantee is possible.

See `Other Files/Documentation/MAX_KNOWLEDGE_ARCHITECTURE.md` for the complete routing and timing design.

</details>

<a id="hardware-combination-matrix"></a>

<details>
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
* selected emergency 135M, 0.6B, 0.8B, 1.5B, 1.7B, 2B, 3.09B, 4B, or 8B model tier

Representative automatic combinations:

| Phone state | Selected stack | Runtime behavior |
| :-- | :-- | :-- |
| **512 MB–1.5 GB or 32-bit** | Internal engine + Micro/Lite | No GGUF; smallest memory footprint |
| **1.5–3 GB or severe pressure** | 135M emergency Q2/Q4 | Emergency-only compact context |
| **Capable 3–4 GB, 64-bit** | Qwen3 0.6B Fast | Normal minimum with guarded context |
| **Strong 4 GB / typical 6 GB** | Qwen3.5 0.8B Quality | Compact quality route |
| **Capable 5–6 GB** | Qwen2.5 1.5B Smart | Advanced compact route |
| **Capable 6–8 GB** | Qwen3 1.7B Ultra | Strongest compact route and adjacent fusion |
| **Strong 8–12 GB** | Qwen3 4B Pro | Guarded high-tier inference |
| **12 GB+ with high live headroom** | Qwen3 8B Max | Flagship guarded inference |

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
| **RAM** | Around 512 MB for the internal engine | 3–4 GB+ for the normal 0.6B tier; 135M remains an emergency fallback |
| **Storage** | Enough for Python and the repository | At least 2 GB free for the 0.6B tier, knowledge indexes, llama.cpp build files, and saves |
| **Internet** | Not needed for normal offline chat | Needed only for installation, Git LFS, or explicit web learning |

### Hardware behavior

* 32-bit or severely constrained devices use the internal bilingual engine.
* Approximately 1–3 GB or severely pressured devices use the internal engine or 135M emergency models.
* Capable 3–4 GB 64-bit devices can start with Qwen3 0.6B when enough RAM is currently free.
* Stronger 4–8 GB devices can progress through real 0.8B, 1.5B, and 1.7B tiers.
* High-end devices can use optional 4B or 8B models with guarded context.
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

<details>
<summary><strong>School Tutor: Grades 1–12</strong></summary>

The school foundation is **shared across every model profile**. This means the internal engine, Fast GGUF, Quality GGUF, and hybrid modes all use the same school tools before generic language-model fallback.

The current school database contains **771 core topics** and **3,994 grade-adapted lesson records**. Each detailed lesson can provide a learning goal, prerequisites, a core explanation, a teaching strategy, vocabulary, a worked or guided example, a common misconception, practice, a mastery check, related topics, and local evidence. Ask for a grade and say **“in detail”** when you want the full lesson.

### Covered school areas

* **Mathematics**
&nbsp;&nbsp;&nbsp;&nbsp;● counting and place value  
&nbsp;&nbsp;&nbsp;&nbsp;● addition, subtraction, multiplication, and division  
&nbsp;&nbsp;&nbsp;&nbsp;● fractions, decimals, percentages, ratios, and proportions  
&nbsp;&nbsp;&nbsp;&nbsp;● factors, multiples, GCD, and LCM  
&nbsp;&nbsp;&nbsp;&nbsp;● integers, exponents, and scientific notation  
&nbsp;&nbsp;&nbsp;&nbsp;● algebra and linear equations  
&nbsp;&nbsp;&nbsp;&nbsp;● quadratic equations  
&nbsp;&nbsp;&nbsp;&nbsp;● coordinates and linear functions  
&nbsp;&nbsp;&nbsp;&nbsp;● geometry, perimeter, area, circles, volume, and Pythagorean theorem  
&nbsp;&nbsp;&nbsp;&nbsp;● mean, median, mode, range, statistics, and probability  
&nbsp;&nbsp;&nbsp;&nbsp;● trigonometry, functions, vectors, and introductory calculus  
* **Science**
&nbsp;&nbsp;&nbsp;&nbsp;● living things, plants, animals, ecosystems, and human body systems  
&nbsp;&nbsp;&nbsp;&nbsp;● matter, atoms, elements, periodic table, reactions, acids, and bases  
&nbsp;&nbsp;&nbsp;&nbsp;● cells, DNA, genetics, evolution, and ecology  
&nbsp;&nbsp;&nbsp;&nbsp;● forces, motion, Newton’s laws, energy, electricity, circuits, and waves  
&nbsp;&nbsp;&nbsp;&nbsp;● weather, climate, rocks, water cycle, Earth systems, and Solar System  
&nbsp;&nbsp;&nbsp;&nbsp;● scientific method and evidence  
* **English and Greek language**
&nbsp;&nbsp;&nbsp;&nbsp;● sentences, subjects, predicates, and parts of speech  
&nbsp;&nbsp;&nbsp;&nbsp;● verb tenses and grammar  
&nbsp;&nbsp;&nbsp;&nbsp;● paragraph and essay structure  
&nbsp;&nbsp;&nbsp;&nbsp;● summaries, vocabulary, argumentation, and evidence  
&nbsp;&nbsp;&nbsp;&nbsp;● literary devices and literature analysis  
&nbsp;&nbsp;&nbsp;&nbsp;● research writing, sources, citations, and plagiarism awareness  
* **History, Geography, and Civics**
&nbsp;&nbsp;&nbsp;&nbsp;● maps, directions, continents, oceans, landforms, and population  
&nbsp;&nbsp;&nbsp;&nbsp;● Ancient Greece, Ancient Rome, Byzantium, Renaissance, and Industrial Revolution  
&nbsp;&nbsp;&nbsp;&nbsp;● World Wars and modern history foundations  
&nbsp;&nbsp;&nbsp;&nbsp;● democracy, constitutions, rights, duties, institutions, and citizenship  
&nbsp;&nbsp;&nbsp;&nbsp;● economics, scarcity, opportunity cost, supply, and demand  
&nbsp;&nbsp;&nbsp;&nbsp;● introductory philosophy and logic  
* **Computing and digital systems**
&nbsp;&nbsp;&nbsp;&nbsp;● hardware, software, operating systems, CPU, memory, files, and storage  
&nbsp;&nbsp;&nbsp;&nbsp;● algorithms, variables, conditions, loops, functions, data structures, testing, and debugging  
&nbsp;&nbsp;&nbsp;&nbsp;● networks, OSI/TCP-IP layers, TCP/UDP, IP, DNS, HTTP/HTTPS, databases, and SQL  
&nbsp;&nbsp;&nbsp;&nbsp;● cybersecurity, encryption, hashing, authentication, malware, phishing, and web safety  
&nbsp;&nbsp;&nbsp;&nbsp;● artificial intelligence, machine learning, neural networks, robotics, software engineering, and digital ethics  
* **Health, life skills, arts, and economics**
&nbsp;&nbsp;&nbsp;&nbsp;● physical and mental wellbeing, first aid, relationships, study habits, time management, budgeting, and career skills  
&nbsp;&nbsp;&nbsp;&nbsp;● drawing, painting, sculpture, photography, design, music, theatre, dance, film, and creative process  
&nbsp;&nbsp;&nbsp;&nbsp;● scarcity, opportunity cost, supply and demand, markets, inflation, banking, taxation, trade, and public policy  

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

### Normal compact GGUF ladder

* **Fast — Qwen3 0.6B Q8_0:** normal minimum for capable 3–4 GB 64-bit phones.
* **Quality — Qwen3.5 0.8B Q4_0:** compact bridge for stronger 4 GB and most 6 GB phones.
* **Smart — Qwen2.5 1.5B Instruct Q4_K_M:** advanced compact tier for capable 5–6 GB phones.
* **Ultra — Qwen3 1.7B Q4_K_M:** strongest compact tier for capable 6–8 GB phones.
* **Pro / Max — Qwen3 4B / 8B Q4_K_M:** optional high-end tiers.

Install the strongest conservative match with `bash "Other Files/install_models.sh"`. Install every compact tier with `bash "Other Files/install_models.sh" --compact`.

### Bundled emergency models

* **Emergency Fast — SmolLM2-135M-Instruct Q2_K**
* **Emergency Quality — SmolLM2-135M-Instruct Q4_1**

The 135M models remain in verified split parts for offline and critical low-memory fallback. They are not the normal Pocket AI 16 starting tier.

### Sequential hybrids

Pocket AI can run adjacent installed models one after another: 135M→0.6B, 0.6B→0.8B, 0.8B→1.5B, 1.5B→1.7B, 1.7B→2B, 2B→3.09B, 3.09B→4B, or 4B→8B. It unloads the analyst before starting the stronger synthesizer, rechecks RAM and temperature, and never adds parameter counts.

### Pre-trained bilingual neural profiles

Micro, Lite, Balanced, Standard, and Max classifiers remain available for routing and fallback. They are not full conversational GGUF models.

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

<a id="conversation-memory-and-web-intelligence"></a>

<details>
<summary><strong>Conversation Memory, Follow-ups, Internet Search And Learning</strong></summary>

Pocket AI now treats chat as a continuing conversation rather than isolated prompts. It restores recent turns at startup, passes prior user/assistant messages into compatible GGUF prompts, resolves short references such as “that,” “why,” “give another example,” and their Greek equivalents, and offers one relevant continuation after substantial explanations.

Web behavior is explicit and controllable:

* `/web auto` searches only when the request is current-sensitive or explicitly asks for online verification.
* `/web on` grounds every suitable question with public web evidence.
* `/web off` keeps all answers offline.
* `/search QUERY` performs a no-key public search and returns readable evidence without saving it.
* `/sources` displays the sources used in the previous web-grounded response.
* `/web-learn QUERY` fetches allowed public pages, splits them into searchable chunks, and saves them in the local SQLite retrieval database.

“Learning” here means durable local retrieval memory, not secretly retraining or changing the GGUF model weights. Stored web knowledge can be searched in later conversations and can be removed with the local data tools. Search providers can fail, rate-limit, change format, or require JavaScript; Pocket AI falls back between DDGS, Bing RSS, and Wikipedia and continues offline when none is available.

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
* `/llm-model fast|quality|smart|ultra|advanced|prime|pro|max`
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
* [Μνήμη Συζήτησης, Συνέχεια και Web Νοημοσύνη](#μνήμη-συζήτησης-συνέχεια-και-web-νοημοσύνη)
* [Google AI και Περιορισμός API Key](#google-ai-και-περιορισμός-api-key)
* [Δομή Φακέλων και Αποθηκεύσεις](#δομή-φακέλων-και-αποθηκεύσεις)
* [Σημαντικές Εντολές](#σημαντικές-εντολές)
* [Ιδιωτικότητα και Ασφάλεια](#ιδιωτικότητα-και-ασφάλεια)
* [Περιορισμοί](#περιορισμοί)
* [Συντελεστές](#συντελεστές)
* [Αποποίηση Ευθύνης](#αποποίηση-ευθύνης)

<a id="κύρια-χαρακτηριστικά"></a>

<details>
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

<details>
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

<details>
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

* **Qwen3 0.6B Fast:** συμπαγής αναβάθμιση συλλογισμού για ικανά 64-bit κινητά με 4 GB+ RAM.
* **Qwen3 1.7B Ultra:** ισχυρότερο τοπικό tier για ικανά κινητά περίπου 6–8 GB RAM.
* **Qwen3 4B Pro:** η πρώτη βαθμίδα που στοχεύει να πλησιάσει εμπειρία σύγχρονου βοηθού σε πολλές συνηθισμένες εργασίες γνώσης και συλλογισμού, για ισχυρά κινητά κατηγορίας 8 GB.
* **Qwen3 8B Max:** η ισχυρότερη υποστηριζόμενη βαθμίδα, για high-end κινητά 12 GB+ με αρκετή ελεύθερη RAM και αποθήκευση.
* **Προστασία μικρού μοντέλου:** ακόμη και με μόνο το 135M παραμένουν ενεργά planner, reranking, exact tools, δίγλωσσο retrieval, validation και ασφαλές fallback.
* **Ειλικρινές όριο δυνατότητας:** τα ενσωματωμένα 135M μοντέλα δεν μπορούν να γίνουν πραγματικά ισάξια με ChatGPT 3.5 μόνο με prompts ή περισσότερα facts. Το Pocket AI τα ενισχύει με retrieval, ακριβή εργαλεία, μνήμη συζήτησης, verification και web grounding και επιλέγει αυτόματα μεγαλύτερο μοντέλο όταν το κινητό μπορεί να το τρέξει με ασφάλεια.

```bash
bash "Other Files/install_smart_models.sh" smart
# Σταδιακά ισχυρότερα και μεγαλύτερα:
bash "Other Files/install_smart_models.sh" ultra
bash "Other Files/install_smart_models.sh" pro
bash "Other Files/install_smart_models.sh" max
```

Μετά χρησιμοποίησε `/μοντέλο smart`, `/μοντέλο ultra` ή άφησε ενεργό το `/υβριδικό auto`.

Ο στόχος των δύο λεπτών αφορά το τοπικό πλάνο inference μετά την εκκίνηση. Η πρώτη ανακατασκευή GGUF, πολύ αργός αποθηκευτικός χώρος, το Android, έντονο thermal throttling ή εξωτερικό build του `llama.cpp` μπορούν να προσθέσουν χρόνο.

</details>

<a id="πίνακας-συνδυασμών-hardware"></a>

<details>
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
* επιλεγμένο emergency 135M ή κανονικό tier 0.6B, 0.8B, 1.5B, 1.7B, 2B, 3.09B, 4B ή 8B

Ενδεικτικοί αυτόματοι συνδυασμοί:

| Κατάσταση κινητού | Επιλεγμένο stack | Συμπεριφορά runtime |
| :-- | :-- | :-- |
| **512 MB–1,5 GB ή 32-bit** | Internal engine + Micro/Lite | Χωρίς GGUF, ελάχιστη μνήμη |
| **1,5–3 GB ή κρίσιμη πίεση** | 135M emergency Q2/Q4 | Emergency context |
| **Ικανό 3–4 GB, 64-bit** | Qwen3 0.6B Fast | Κανονικό ελάχιστο tier |
| **Ισχυρό 4 GB / τυπικό 6 GB** | Qwen3.5 0.8B Quality | Compact ποιοτική λειτουργία |
| **Ικανό 5–6 GB** | Qwen2.5 1.5B Smart | Advanced compact tier |
| **Ικανό 6–8 GB** | Qwen3 1.7B Ultra | Ισχυρότερο compact tier και adjacent fusion |
| **Ισχυρό 8–12 GB** | Qwen3 4B Pro | Guarded high-tier inference |
| **12 GB+ με αρκετή ελεύθερη RAM** | Qwen3 8B Max | Flagship guarded inference |

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
| **RAM** | Περίπου 512 MB για τον εσωτερικό engine | 3–4 GB+ για το κανονικό 0.6B tier· τα 135M είναι emergency fallback |
| **Αποθήκευση** | Αρκετή για Python και repository | Τουλάχιστον 2 GB ελεύθερα για 0.6B, indexes γνώσης, llama.cpp build και saves |
| **Internet** | Δεν χρειάζεται για κανονικό offline chat | Χρειάζεται μόνο για εγκατάσταση, Git LFS ή ρητή web learning λειτουργία |

### Συμπεριφορά ανά hardware

* 32-bit ή πολύ περιορισμένες συσκευές χρησιμοποιούν τον εσωτερικό δίγλωσσο engine.
* Συσκευές περίπου 1–3 GB ή με κρίσιμη πίεση χρησιμοποιούν internal engine ή emergency 135M.
* Ικανές 64-bit συσκευές 3–4 GB μπορούν να ξεκινήσουν από Qwen3 0.6B όταν υπάρχει αρκετή ελεύθερη RAM.
* Ισχυρότερες συσκευές 4–8 GB προχωρούν σε πραγματικά tiers 0.8B, 1.5B, 1.7B, 2B και 3.09B.
* High-end συσκευές μπορούν να χρησιμοποιήσουν προαιρετικά 4B ή 8B με guarded context.
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

<details>
<summary><strong>Σχολικός Βοηθός: Τάξεις 1–12</strong></summary>

Η σχολική βάση είναι **κοινή για κάθε profile μοντέλου**. Ο εσωτερικός engine, το Fast GGUF, το Quality GGUF και τα hybrid modes χρησιμοποιούν τα ίδια σχολικά εργαλεία πριν από γενικό LLM fallback.

Η τρέχουσα σχολική βάση περιέχει **771 βασικά θέματα** και **3.994 προσαρμοσμένα μαθήματα τάξης**. Κάθε αναλυτικό μάθημα μπορεί να δώσει μαθησιακό στόχο, προαπαιτούμενα, βασική εξήγηση, στρατηγική διδασκαλίας, λεξιλόγιο, καθοδηγούμενο παράδειγμα, συνηθισμένη παρανόηση, εξάσκηση, έλεγχο κατάκτησης, σχετικά θέματα και τοπικά τεκμήρια. Γράψε τάξη και **«αναλυτικά»** για πλήρες μάθημα.

### Καλυπτόμενοι τομείς

* **Μαθηματικά**
&nbsp;&nbsp;&nbsp;&nbsp;● μέτρηση και αξία θέσης  
&nbsp;&nbsp;&nbsp;&nbsp;● πρόσθεση, αφαίρεση, πολλαπλασιασμός και διαίρεση  
&nbsp;&nbsp;&nbsp;&nbsp;● κλάσματα, δεκαδικοί, ποσοστά, λόγοι και αναλογίες  
&nbsp;&nbsp;&nbsp;&nbsp;● παράγοντες, πολλαπλάσια, ΜΚΔ και ΕΚΠ  
&nbsp;&nbsp;&nbsp;&nbsp;● ακέραιοι, δυνάμεις και επιστημονική γραφή  
&nbsp;&nbsp;&nbsp;&nbsp;● άλγεβρα και γραμμικές εξισώσεις  
&nbsp;&nbsp;&nbsp;&nbsp;● εξισώσεις δευτέρου βαθμού  
&nbsp;&nbsp;&nbsp;&nbsp;● συντεταγμένες και γραμμικές συναρτήσεις  
&nbsp;&nbsp;&nbsp;&nbsp;● γεωμετρία, περίμετρος, εμβαδόν, κύκλοι, όγκος και Πυθαγόρειο θεώρημα  
&nbsp;&nbsp;&nbsp;&nbsp;● μέσος όρος, διάμεσος, επικρατούσα τιμή, εύρος, στατιστική και πιθανότητες  
&nbsp;&nbsp;&nbsp;&nbsp;● τριγωνομετρία, συναρτήσεις, διανύσματα και εισαγωγικός λογισμός  
* **Επιστήμες**
&nbsp;&nbsp;&nbsp;&nbsp;● ζωντανά, φυτά, ζώα, οικοσυστήματα και ανθρώπινο σώμα  
&nbsp;&nbsp;&nbsp;&nbsp;● ύλη, άτομα, στοιχεία, περιοδικός πίνακας, αντιδράσεις, οξέα και βάσεις  
&nbsp;&nbsp;&nbsp;&nbsp;● κύτταρα, DNA, γενετική, εξέλιξη και οικολογία  
&nbsp;&nbsp;&nbsp;&nbsp;● δυνάμεις, κίνηση, νόμοι Νεύτωνα, ενέργεια, ηλεκτρισμός, κυκλώματα και κύματα  
&nbsp;&nbsp;&nbsp;&nbsp;● καιρός, κλίμα, πετρώματα, κύκλος νερού, Γη και Ηλιακό Σύστημα  
&nbsp;&nbsp;&nbsp;&nbsp;● επιστημονική μέθοδος και τεκμήρια  
* **Ελληνική και Αγγλική γλώσσα**
&nbsp;&nbsp;&nbsp;&nbsp;● προτάσεις, υποκείμενο, κατηγόρημα και μέρη του λόγου  
&nbsp;&nbsp;&nbsp;&nbsp;● χρόνοι ρημάτων και γραμματική  
&nbsp;&nbsp;&nbsp;&nbsp;● δομή παραγράφου και έκθεσης  
&nbsp;&nbsp;&nbsp;&nbsp;● περιλήψεις, λεξιλόγιο, επιχειρηματολογία και τεκμήρια  
&nbsp;&nbsp;&nbsp;&nbsp;● λογοτεχνικά σχήματα και ανάλυση λογοτεχνίας  
&nbsp;&nbsp;&nbsp;&nbsp;● έρευνα, πηγές, παραπομπές και αποφυγή λογοκλοπής  
* **Ιστορία, Γεωγραφία και Αγωγή Πολίτη**
&nbsp;&nbsp;&nbsp;&nbsp;● χάρτες, κατευθύνσεις, ήπειροι, ωκεανοί, ανάγλυφο και πληθυσμός  
&nbsp;&nbsp;&nbsp;&nbsp;● Αρχαία Ελλάδα, Αρχαία Ρώμη, Βυζάντιο, Αναγέννηση και Βιομηχανική Επανάσταση  
&nbsp;&nbsp;&nbsp;&nbsp;● Παγκόσμιοι Πόλεμοι και βασικές έννοιες νεότερης ιστορίας  
&nbsp;&nbsp;&nbsp;&nbsp;● δημοκρατία, σύνταγμα, δικαιώματα, υποχρεώσεις, θεσμοί και πολίτες  
&nbsp;&nbsp;&nbsp;&nbsp;● οικονομικά, σπανιότητα, κόστος ευκαιρίας, προσφορά και ζήτηση  
&nbsp;&nbsp;&nbsp;&nbsp;● εισαγωγή σε φιλοσοφία και λογική  
* **Πληροφορική και δεξιότητες μελέτης**
&nbsp;&nbsp;&nbsp;&nbsp;● hardware, software, είσοδος, έξοδος και αποθήκευση  
&nbsp;&nbsp;&nbsp;&nbsp;● αλγόριθμοι, μεταβλητές, συνθήκες, βρόχοι, συναρτήσεις, testing και debugging  
&nbsp;&nbsp;&nbsp;&nbsp;● ψηφιακή ασφάλεια, αξιοπιστία πηγών και media literacy  
&nbsp;&nbsp;&nbsp;&nbsp;● ενεργή ανάκληση, κατανεμημένη επανάληψη, λυμένα παραδείγματα και πρόγραμμα μελέτης  

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

### Κανονική compact κλίμακα

* **Fast — Qwen3 0.6B Q8_0:** κανονικό ελάχιστο tier.
* **Quality — Qwen3.5 0.8B Q4_0:** ενδιάμεσο compact tier.
* **Smart — Qwen2.5 1.5B Instruct Q4_K_M:** ισχυρότερο instruction tier.
* **Ultra — Qwen3 1.7B Q4_K_M:** ισχυρότερο compact tier.
* **Pro / Max — Qwen3 4B / 8B Q4_K_M:** προαιρετικά high-end tiers.

Η κανονική εγκατάσταση επιλέγει το ισχυρότερο ασφαλές tier. Με `bash "Other Files/install_models.sh" --compact` εγκαθίστανται όλα τα tiers από 0.6B έως 3.09B.

### Emergency μοντέλα

* **Emergency Fast — SmolLM2-135M-Instruct Q2_K**
* **Emergency Quality — SmolLM2-135M-Instruct Q4_1**

Τα 135M παραμένουν για offline ή κρίσιμη low-memory λειτουργία και δεν είναι πλέον η κανονική αρχή.

### Διαδοχικά hybrids

Τα routes 0.6B→0.8B, 0.8B→1.5B, 1.5B→1.7B, 1.7B→2B και 2B→3.09B εκτελούνται διαδοχικά. Το πρώτο μοντέλο κλείνει πριν ανοίξει το ισχυρότερο. Οι παράμετροι δεν αθροίζονται.

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
* `/μοντέλο fast|quality|smart|ultra|advanced|prime|pro|max`
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
* Καμία πεπερασμένη offline βάση δεν περιέχει κάθε πρόταση από κάθε σχολικό βιβλίο. Η παρούσα βάση καλύπτει 771 θέματα και 3.994 αναλυτικά μαθήματα τάξης, αλλά δεν ισχυρίζεται ότι αντιγράφει κάθε εθνικό πρόγραμμα ή εξεταστικό φορέα.
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
