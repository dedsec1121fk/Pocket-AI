Pocket AI 15 — Compact Hybrid Intelligence
===========================================

Run from the repository root:
  python "Pocket AI.py"

Normal startup enters chat directly. Type help or βοήθεια for the easy menu.

NORMAL MODEL LADDER
-------------------
- fast: Qwen3 0.6B Q8_0 (normal minimum)
- quality: Qwen3.5 0.8B Q4_0
- smart: Qwen2.5 1.5B Instruct Q4_K_M
- ultra: Qwen3 1.7B Q4_K_M
- pro/max: optional Qwen3 4B / 8B

EMERGENCY FALLBACKS
-------------------
- emergency_fast: SmolLM2 135M Q2_K
- emergency_quality: SmolLM2 135M Q4_1
The bundled 135M files are retained for critical memory, offline, or unsupported
conditions; they are no longer the normal starting tier.

INSTALLATION
------------
- `bash "Other Files/install_models.sh"` reconstructs emergency models, selects
  the strongest conservative regular model for this phone, and builds llama.cpp.
- `bash "Other Files/install_models.sh" --compact` installs all four compact
  regular tiers from 0.6B through 1.7B.
- Downloads resume and are checked against repository metadata, exact byte size,
  SHA-256, and the GGUF header.

HYBRID EXECUTION
----------------
Adjacent installed tiers can run sequentially. The first model is unloaded before
the stronger model starts. Parameter counts are never added together, and only one
GGUF process remains resident at a time.

FOLDERS
-------
- Models/: classifiers, specialists, controllers, knowledge shards, and optional GGUFs.
- Models/GGUF Parts/: verified parts for the two emergency 135M models.
- Other Files/Modules/: standard-library runtime modules.
- Other Files/Saved Data/: settings, memories, indexed knowledge, history, and runtime cache.

SHARED KNOWLEDGE
----------------
- 12,842 English/Greek maximum-knowledge records and 78,509 aliases.
- 771 school topics and 3,994 grade-adapted lessons for grades 1–12.
- 117,659 WordNet concepts and 68,342 offline encyclopedia passages.
- Retrieval learning does not mutate GGUF weights.

See README.md and Documentation/COMPACT_HYBRID_MODEL_LADDER.md for details.
