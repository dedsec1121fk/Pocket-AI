# Pocket AI 15.0 — Compact Hybrid Model Ladder

Pocket AI now treats **0.6B as the normal minimum local language-model tier**. The two bundled SmolLM2 135M models remain available only as emergency fallbacks for severe memory pressure, unsupported installations, offline setup, or very old hardware.

## Real model tiers

| Pocket AI key | Real model | Parameters | Role |
|---|---|---:|---|
| `emergency_fast` | SmolLM2 135M Q2_K | 134.52M | minimum-memory emergency fallback |
| `emergency_quality` | SmolLM2 135M Q4_1 | 134.52M | higher-precision emergency fallback |
| `fast` | Qwen3 0.6B Q8_0 | 0.6B | normal minimum and fast compact tier |
| `quality` | Qwen3.5 0.8B Q4_0 | 0.8B | bridge between 0.6B and 1.5B |
| `smart` | Qwen2.5 1.5B Instruct Q4_K_M | about 1.5B | advanced compact instruction tier |
| `ultra` | Qwen3 1.7B Q4_K_M | 1.7B | strongest compact tier |
| `pro` | Qwen3 4B Q4_K_M | 4B | optional advanced tier |
| `max` | Qwen3 8B Q4_K_M | 8B | optional maximum tier |

The 0.8B and 1.5B entries are actual model sizes, not invented labels. Pocket AI does not pretend that a hybrid creates a new model size.

## Sequential hybrid routes

Hybrid mode uses adjacent installed tiers:

- `emergency_quality → fast`
- `fast → quality` (0.6B → 0.8B)
- `quality → smart` (0.8B → 1.5B)
- `smart → ultra` (1.5B → 1.7B)
- `ultra → pro`
- `pro → max`

The first model produces a compact evidence-grounded analysis. Pocket AI unloads it, rechecks live RAM and temperature, then starts the stronger model only when the second pass remains safe. Only one GGUF process is resident at a time. Parameter counts are **not additive**: a 0.6B → 0.8B route remains two sequential models, not a 1.4B model.

## Installation

The normal installer selects the strongest conservative regular tier:

```bash
bash "Other Files/install_models.sh"
```

Install every compact tier from 0.6B through 1.7B:

```bash
bash "Other Files/install_models.sh" --compact
```

Direct tier choices:

```bash
bash "Other Files/install_models.sh" --0.6b
bash "Other Files/install_models.sh" --0.8b
bash "Other Files/install_models.sh" --1.5b
bash "Other Files/install_models.sh" --1.7b
```

Use `--emergency-only` only when the phone cannot safely install a regular tier or the installation must stay completely offline.

## Conservative phone bands

These bands are starting points, not guarantees. Pocket AI also checks live free RAM, 64-bit support, CPU score, storage, battery, temperature, task complexity, and the remaining answer deadline.

| Device state | Preferred tier |
|---|---|
| Severe pressure, under about 3 GB total RAM, or no regular model installed | 135M emergency fallback |
| Capable 3–4 GB 64-bit phone with enough live free RAM | 0.6B |
| Strong 4 GB or typical 6 GB phone | 0.8B |
| Capable 5–6 GB phone | 1.5B |
| Capable 6–8 GB phone | 1.7B |
| Strong 8 GB-class phone | 4B only when live headroom is sufficient |
| High-end 12 GB+ phone | 8B only when live headroom is sufficient |

A Galaxy A22-class device therefore normally falls between 0.6B and 1.7B depending on its RAM configuration and current free memory.

## Capability boundary

More parameters generally improve instruction following, language generation, coding, and reasoning, but parameter count alone does not determine quality. Architecture, training, instruction tuning, quantization, context, retrieval, exact tools, and orchestration also matter. Pocket AI uses those supporting systems aggressively, but does not claim that any small local model literally equals GPT-3.5.
