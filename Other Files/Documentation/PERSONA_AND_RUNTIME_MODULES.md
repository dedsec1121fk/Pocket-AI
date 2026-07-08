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
- **consensus**: independent Fast and Quality answers are generated sequentially and scored.

All multi-model paths are sequential to limit peak RAM.
