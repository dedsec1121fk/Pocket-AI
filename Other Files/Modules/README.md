# Pocket AI Runtime Modules

These standard-library modules are loaded by `Pocket AI.py` and provide real runtime behavior:

- `persona_engine.py` — persistent AI name, user name, conversational style, and safe natural-language polishing.
- `context_optimizer.py` — selects the most relevant local knowledge, memories, and recent conversation under a strict character budget.
- `consensus_engine.py` — compares a compact draft with a stronger verification answer in sequential consensus mode.
- `confidence_engine.py` — calibrates answer confidence from the route, neural score, and response-quality result.
- `resource_advisor.py` — turns hardware scan data into a concise model-selection explanation.

They use only Python's standard library and remain optional: the main script contains safe fallbacks if a module is missing.

- `school_tutor.py` — shared English/Greek grade 1-12 knowledge retrieval plus deterministic arithmetic, fractions, percentages, equations, statistics, and geometry.

## Version 20 modules

- `universal_knowledge.py` — common bilingual knowledge for every AI route.
- `conversation_engine.py` — natural small talk and follow-up resolution.
- `resource_matrix.py` — continuous Android hardware tuning across realistic RAM/CPU combinations.

## Maximum-knowledge modules

- `lexical_knowledge.py` — read-only English/Greek WordNet retrieval over seven SQLite FTS5 shards.
- `encyclopedia_knowledge.py` — exact-title and full-text retrieval over five offline Simple English encyclopedia shards; injects only compact passages and flags time-sensitive queries.

All ten runtime modules use Python's standard library. Knowledge databases remain immutable and are opened with low cache limits for old Android devices.

- `smart_reasoning.py`: task classification, query variants, sentence-level evidence ranking, compact grounding packets, extractive fallback, and output validation.


### `advanced_reasoning.py`

The high-precision reasoning layer. It performs query decomposition, comparison balancing, source-prior evidence diagnostics, exact arithmetic/algebra/statistics/conversion tools, grounded deterministic synthesis, answer auditing, language checks, prompt-leak detection, and generated-versus-grounded repair. It is standard-library-only and improves even the 135M emergency models without adding model inference latency.


## Natural Complete School modules

- `school_tutor.py`: searches the 771-topic / 3,994-lesson curriculum database, detects grade and requested depth, formats detailed bilingual lessons, and handles deterministic school mathematics.
- `conversation_engine.py`: bilingual social intent, follow-up resolution, confusion recovery, and natural generation guidance.
- `persona_engine.py`: persistent speaking style plus conservative boilerplate and repetition cleanup.
- `smart_reasoning.py`: identifies detailed and school requests so retrieval, synthesis, and output budgets are adjusted.

- `web_intelligence.py`: detects current/explicit web requests, cleans queries, controls off/auto/on behavior, and formats source lists.

## MaxSafe runtime modules

● `thermal_governor.py` classifies battery, skin, and SoC sensor readings; estimates model working sets; tunes context/batch/threads; monitors active inference; and protects a live Android RAM reserve.

● `hybrid_orchestrator.py` chooses the strongest safe installed model and builds sequential analyst/synthesizer fusion plans for difficult questions. It never requires two GGUF processes to be resident at once.

- `adaptive_compute.py` — persistent per-model speed/heat learning, deadline-aware token budgets, and safe cool-device burst tuning.


POCKET AI 14.0 SPEC-MAX COGNITIVE SCALING
- Parallel cached web search and page reading.
- `/learn safe` for trusted automatic learning; `/learn fast` for more aggressive parallel page learning.
- `shared_learning.py` shares verified lessons across all model tiers.
- `model_intelligence.py` gives each model tier an evidence-first instruction profile.
- This is retrieval learning, not unsafe GGUF weight mutation.

## Pocket AI 14.0 Spec-Max modules

- `model_intelligence.py` version 2 — separate instructions, evidence compression, task-aware sampling, and output budgeting for Fast, Quality, Smart, Ultra, Pro, and Max.
- `resource_matrix.py` version 7 — expanded realistic combinations plus the new `flagship` runtime profile.
- The main pipeline resolves the target model before building context, so evidence and output budgets are calculated for the model that will actually answer.
