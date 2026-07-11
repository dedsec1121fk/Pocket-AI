Pocket AI
=========

Run from the repository root:
  python "Pocket AI.py"

Normal startup enters chat directly. Type help or βοήθεια for the easy menu.

Folders:
- Models/ contains bundled classifiers, specialists, school packs, controllers, and split GGUF packages.
- Models/GGUF Parts/ contains the Q2_K and Q4_1 models as verified parts; every part is below 60 MB.
- Other Files/Modules/ contains standard-library runtime modules.
- Other Files/Saved Data/ contains generated settings, memory, learned knowledge, scans, history, exports, and runtime files.
- Other Files/Saved Data/GGUF Models/ is the automatic reconstruction cache used by llama.cpp.

Model preparation:
- Pocket AI reconstructs the selected GGUF automatically on first use.
- Run `bash "Other Files/install_models.sh"` to reconstruct both models, verify them, and build llama.cpp in advance.
- Runtime GGUF files can be deleted safely; the verified package parts remain in Models/GGUF Parts/.

School support:
- Shared grades 1-12 foundation in English and Greek.
- Use /school, /school 5 math, or /school 9 science.

Web learning:
- /web-learn and /dork use safe public Bing RSS, Wikipedia, and readable pages without an API key.
- Official Google Gemini access is not bypassed and requires credentials.

See the root README.md for complete English and Greek documentation.

Split GGUF edition:
- Q2_K and Q4_1 weights are included without downloading AI weights.
- Maximum packaged part size: 48 MiB.
- Per-part and complete-model SHA-256 verification.
- Atomic reconstruction prevents incomplete runtime models.

Max knowledge edition: 12,842 English/Greek records, 78,509 aliases, SQLite FTS5 retrieval, compact model context, and safe response caching.

Maximum-knowledge additions:
- Models/Lexical Knowledge: 117,659 WordNet concepts with Greek links.
- Models/Encyclopedia Knowledge: 45,591 offline articles / 68,342 FTS passages.
- Modules/lexical_knowledge.py and encyclopedia_knowledge.py perform low-RAM retrieval.
- All local inference passes share a 112-second plan; actual full wall time can vary by device and first-run setup.


NATURAL COMPLETE SCHOOL BUILD 9.0
- 771 searchable grade 1-12 topics
- 3,994 grade-adapted detailed lesson records
- English and Greek grade/depth detection
- natural contextual follow-ups, examples, analogies, quizzes, and confusion recovery
- school SQLite FTS5 database: Models/School Knowledge/PocketAI_School_Curriculum.sqlite3

MAXSAFE 11.0
- Modules/thermal_governor.py: live thermal/RAM governor.
- Modules/hybrid_orchestrator.py: strongest-safe model selection and sequential fusion.
- install_models.sh --best: builds llama.cpp and downloads the strongest practical optional model for the current phone.
- Documentation/MAXSAFE_THERMAL_HYBRID.md: architecture and safety limits.

Pocket AI 12.0 Adaptive MaxSafe: runtime_telemetry.json stores local per-model speed and heat-response measurements. It is safe to delete; Pocket AI will relearn conservative defaults.


POCKET AI 14.0 SPEC-MAX COGNITIVE SCALING
- Parallel cached web search and page reading.
- `/learn safe` for trusted automatic learning; `/learn fast` for more aggressive parallel page learning.
- `shared_learning.py` shares verified lessons across all model tiers.
- `model_intelligence.py` gives each model tier an evidence-first instruction profile.
- This is retrieval learning, not unsafe GGUF weight mutation.
