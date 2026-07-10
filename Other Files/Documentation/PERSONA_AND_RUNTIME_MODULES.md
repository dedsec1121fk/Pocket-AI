# Persona and Runtime Modules

Pocket AI loads optional standard-library modules from `Other Files/Modules/`.

## Persistent persona

The launcher option **Name & Humanize AI** writes `Other Files/Saved Data/persona.json` with:

- assistant name
- optional user name
- style (`friendly`, `calm_expert`, `casual`, `mentor`, or `direct`)
- natural-wording switch

The assistant remains explicitly an AI. The feature changes tone and wording, not identity claims.

## New hybrid modes

- **adaptive**: Fast first; Quality is run only when the first answer or question complexity requires it.
- **expert**: specialist instructions + optimized local context + Quality GGUF.
- **consensus**: a compact draft and a stronger verification answer are generated sequentially and scored.

All multi-model paths are sequential to limit peak RAM.

## Universal and continuous runtime modules

- `universal_knowledge.py` loads the shared English/Greek knowledge foundation before any transformer fallback.
- `conversation_engine.py` handles small talk and follow-up context without pretending the AI is human.
- `resource_matrix.py` continuously tunes model choice, classifier capacity, hybrid mode, threads, context, batch, micro-batch, and output length.
- `HARDWARE_COMBINATIONS.md` documents representative RAM/CPU/bitness combinations.
