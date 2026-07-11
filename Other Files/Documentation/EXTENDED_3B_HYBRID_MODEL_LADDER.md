# Pocket AI 16.0 Extended 3B Hybrid Model Ladder

## Normal tiers

| Tier | Model | Parameters | Default quantization | Role |
|---|---|---:|---|---|
| Fast | Qwen3 | 0.6B | Q8_0 | minimum normal generator |
| Quality | Qwen3.5 | 0.8B | Q4_0 | compact quality bridge |
| Smart | Qwen2.5 Instruct | 1.54B | Q4_K_M | general reasoning |
| Ultra | Qwen3 | 1.7B | Q4_K_M | stronger instruction and reasoning |
| Advanced | Qwen3.5 | 2B | Q4_K_M | capable 6–8 GB phones |
| Prime | Qwen2.5 Instruct | 3.09B | Q3_K_M or Q4_K_M | maximum extended tier |

Optional Pro 4B and Max 8B remain available for high-memory phones. SmolLM2 135M Q2_K/Q4_1 are emergency-only.

## Sequential hybrids

`0.6B→0.8B`, `0.8B→1.5B`, `1.5B→1.7B`, `1.7B→2B`, and `2B→3.09B`. The first model is fully unloaded before the second starts. Parameter counts are not additive.

## Safety

Model selection uses total and available RAM, CPU score, 64-bit capability, free storage, thermal state, battery state, task complexity, and remaining deadline. A model-loading failure triggers a lower-tier retry.
