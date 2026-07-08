# Pocket AI Runtime Modules

These standard-library modules are loaded by `Pocket AI.py` and provide real runtime behavior:

- `persona_engine.py` — persistent AI name, user name, conversational style, and safe natural-language polishing.
- `context_optimizer.py` — selects the most relevant local knowledge, memories, and recent conversation under a strict character budget.
- `consensus_engine.py` — compares independent Fast and Quality GGUF answers in sequential consensus mode.
- `confidence_engine.py` — calibrates answer confidence from the route, neural score, and response-quality result.
- `resource_advisor.py` — turns hardware scan data into a concise model-selection explanation.

They use only Python's standard library and remain optional: the main script contains safe fallbacks if a module is missing.

- `school_tutor.py` — shared English/Greek grade 1-12 knowledge retrieval plus deterministic arithmetic, fractions, percentages, equations, statistics, and geometry.
