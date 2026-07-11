Pocket AI 16.0 — Extended 3B Hybrid Intelligence

Normal model ladder:
  fast 0.6B -> quality 0.8B -> smart 1.5B -> ultra 1.7B -> advanced 2B -> prime 3.09B
Optional high-memory tiers: pro 4B and max 8B.
Bundled SmolLM2 135M models are emergency/offline fallbacks only.

Install strongest safe tier:
  bash "Other Files/install_models.sh"
Install all normal tiers through 3.09B:
  bash "Other Files/install_models.sh" --extended

Hybrid routes are sequential. Only one GGUF model is resident at a time, and parameter counts are not additive. Live RAM, CPU, storage, thermal pressure, battery state, task complexity, and deadline control routing.
