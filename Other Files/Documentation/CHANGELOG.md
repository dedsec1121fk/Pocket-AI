# Changelog

## 7.0 — advanced reasoning and Qwen3

- Added `advanced_reasoning.py` with query decomposition, exact local solvers, evidence diagnostics, grounded synthesis, and answer auditing/repair.
- Upgraded optional local reasoning tiers to Qwen3 0.6B Q8_0 Smart and Qwen3 1.7B Q8_0 Ultra.
- Added adaptive Qwen3 thinking/non-thinking prompting and removal of hidden reasoning tags.
- Added official Hugging Face LFS SHA-256 and size verification to the resumable Termux downloader.
- Added comparison-side coverage checks, wrong-language correction, unsupported-number checks, and deterministic fallback selection.
- Preserved the shared 112-second local inference plan and sub-60-MB packaged-file rule.

## 6.1 — Bilingual reasoning and comparison repair

- Added Greek-to-English encyclopedia and WordNet query bridging.
- Added entity-balanced retrieval for comparisons such as TCP versus UDP.
- Added reviewed bilingual expert responses for common networking, security, hardware, and science questions.
- Improved evidence relevance filtering, answer validation, and safe fallback behavior.
- Corrected live hardware combination reporting for each active model tier.
- Added optional Qwen2.5 0.5B Smart and 1.5B Ultra model routes with guarded runtime plans.

# Pocket AI Changelog

## Smart Reasoning + Qwen Upgrade Edition

- Added task classification, query expansion, sentence-level evidence reranking, compact evidence packets, extractive fallback, and answer validation.
- Reworked the answer pipeline so even the 135M models synthesize only high-value evidence instead of receiving loosely related passages.
- Added Qwen2.5 0.5B Smart and Qwen2.5 1.5B Ultra optional model tiers with official resumable downloads and exact SHA-256 verification.
- Added hardware-aware selection across Fast, Quality, Smart, and Ultra while keeping one GGUF process in memory.
- Added stricter factual, arithmetic, code, command, language, relevance, and repetition checks.
- Preserved the shared 112-second generation plan and deterministic fallback when a model times out or produces low-quality text.

## Maximum Smartness Retrieval Edition

- Added 117,659 WordNet concepts, 206,978 English lemma records, 17,891 Greek-linked concepts, and 23,853 Greek lemma records.
- Added 45,591 offline encyclopedia articles split into 68,342 searchable passages and five immutable FTS5 shards.
- Added exact-title encyclopedia extracts for static English topics and evidence injection for broader questions.
- Rebalanced tiny-model context so curated facts, encyclopedia passages, and lexical evidence compete for a strict prompt budget.
- Enlarged guarded context windows for low-end Q2_K profiles while retaining RAM and thermal downgrades.
- Set a shared 112-second local-inference plan and a 106-second subprocess ceiling.
- Restricted multi-pass reasoning to devices that can afford it; low-end profiles use one evidence-rich pass.
- Changed automatic local-LLM mode to `always` whenever a valid bundled GGUF runner is available.
- Added provenance, attribution, licensing notices, and package-wide sub-60 MB knowledge shards.

## Max Knowledge Indexed Edition

## 4.1 — Split GGUF distribution

- Added the verified Q2_K and Q4_1 SmolLM2 GGUF weights to the package.
- Split each GGUF into two ordered parts with a 48 MiB maximum part size.
- Added `Models/GGUF Parts/split_models_manifest.json` with exact part sizes and SHA-256 hashes.
- Added automatic, atomic model reconstruction and runtime-cache reuse in `Pocket AI.py`.
- Updated the Termux installer to reconstruct and verify both GGUF models without downloading weights.
- Updated English and Greek documentation and model manifests.

- Expanded the shared English/Greek knowledge foundation from 274 to 12,775 records.
- Added 78,149 normalized aliases across 51 categories.
- Added a read-only SQLite FTS5 index for fast low-RAM retrieval.
- Connected the same knowledge bridge to classifiers, specialists, MicroLM, and GGUF inference.
- Added compact knowledge context injection, relevance reranking, prompt compression, and safe static-answer caching.
- Exact facts and mathematics can bypass transformer generation for faster responses.

# Pocket AI Changelog

## Direct Chat + Simple Help Edition

- Removed the launcher from normal startup.
- Pocket AI now opens directly at the `You:` / `Εσύ:` chat prompt.
- Typing `help`, `/help`, `βοήθεια`, or `/βοήθεια` opens a simple numbered menu.
- Added natural phrases such as `scan my phone`, `find best model`, `change your name`, and `exit`.
- Added menu-driven teaching, file learning, safe web research, phone scanning, model status, and persona setup.
- Added a compact bilingual common-knowledge layer for reliable everyday definitions even when llama.cpp is not installed.
- Kept automatic phone scanning and resource-aware model selection in the background.
- Reduced technical startup output so the program waits for a normal question.

## Human Persona + Expanded Hybrid Edition

- Added main-menu option **Name & Humanize AI**.
- Added persistent AI name, optional user name, five conversation styles, and a natural-wording switch.
- Added `/persona`, `/name`, `/style`, and `/human` with Greek aliases.
- Added `adaptive`, `expert`, and `consensus` hybrid modes.
- Added a sequential consensus engine that compares independent Fast and Quality answers.
- Added prompt-context optimization for documents, memories, and recent conversation.
- Added route-aware answer confidence calibration.
- Added a resource-selection explanation module.
- Expanded hybrid control files from four to nine.
- Added a full GitHub-ready English/Greek `README.md`.
- Preserved all models, classifiers, specialists, licenses, saved-data separation, and no-root Termux support from the previous package.


## Grade 1-12 School + No-Key Learning Edition

- Added a shared bilingual school foundation used before every model fallback.
- Added 79 curriculum concepts across mathematics, science, English/Greek language, history, geography, civics, economics, computing, and study skills.
- Added deterministic arithmetic, fraction, percentage, statistics, GCD/LCM, equation, and geometry solvers.
- Added five school specialist models and a school hybrid controller.
- Added `/school` and a school option in the easy `help` menu.
- Added Bing RSS + Wikipedia no-key public learning with safe dork validation.
- Added `/google-ai` to explain honestly that official Gemini access requires credentials.
- Rebuilt the root README as a full bullet-based English/Greek GitHub document.

## Version 20 — Universal Knowledge and Continuous Phone Tuning

- Added a 274-entry English/Greek universal knowledge foundation shared by every model path.
- Added natural bilingual small talk and follow-up resolution.
- Added continuous CPU/RAM/storage/temperature/battery runtime tuning.
- Added representative hardware combinations from sub-1 GB internal mode through 8 GB consensus mode.
- Fixed the Termux llama.cpp installer so current tool-target layouts build `llama-cli` reliably.
- Added `/knowledge` and `/γνώσεις`.
- Preserved one-GGUF-process-at-a-time behavior.


## 9.0 — Natural Complete School

- Expanded the school foundation to 758 concepts and 3,893 grade-adapted lessons.
- Added a read-only FTS5 school curriculum database with structured goals, prerequisites, explanations, strategies, vocabulary, examples, misconceptions, practice, mastery checks, relationships, and evidence.
- Added grade and requested-depth detection in English and Greek.
- Added natural follow-up modes for simpler, deeper, example, analogy, why/how, and quiz requests.
- Added confusion recovery that changes the teaching method.
- Improved persona prompting and removed canned boilerplate and repeated lines.
- Increased evidence and answer budgets for detailed and school questions while retaining the shared answer deadline.
- Added exact-title school retrieval and simple Greek inflection matching.
