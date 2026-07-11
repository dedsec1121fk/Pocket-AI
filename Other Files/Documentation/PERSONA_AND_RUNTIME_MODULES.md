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

- **adaptive**: selects a safe regular tier and escalates only to its immediately stronger installed neighbor when needed.
- **expert**: specialist guidance, compressed evidence, and the strongest safe model.
- **consensus**: adjacent installed tiers generate answers sequentially and are scored.
- **fusion/cascade**: supported routes are 0.6B→0.8B, 0.8B→1.5B, 1.5B→1.7B, 1.7B→4B, and 4B→8B, with emergency 135M→0.6B when necessary.

All multi-model paths are sequential to limit peak RAM. Parameter counts are not added together.

## Universal and continuous runtime modules

- `universal_knowledge.py` loads the shared English/Greek knowledge foundation before any transformer fallback.
- `conversation_engine.py` handles small talk and follow-up context without pretending the AI is human.
- `resource_matrix.py` continuously tunes model choice, classifier capacity, hybrid mode, threads, context, batch, micro-batch, and output length.
- `HARDWARE_COMBINATIONS.md` documents representative RAM/CPU/bitness combinations.
