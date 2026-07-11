# Pocket AI 15.0 Hardware Combination Matrix

Pocket AI measures live resources; advertised RAM alone is not enough. These rows are conservative starting points, not device guarantees.

| Total RAM / live state | Free RAM | CPU score | Bitness | Recommended language tier | Runtime profile | Hybrid policy |
|---|---:|---:|:---:|---|---|---|
| 0.5–1.5 GB | 90–280 MB | 0–20 | 32/64 | internal classifiers and retrieval only | `ultra_eco` | off |
| 1.5–3 GB or critical pressure | 280–700 MB | 14–40 | 64 | 135M emergency Q2/Q4 | `eco` / `entry` | speed |
| Capable 3–4 GB | 800 MB+ | 24–55 | 64 | Qwen3 0.6B Q8_0 | `entry` / `balanced` | smart |
| Strong 4 GB / typical 6 GB | 950 MB+ | 30–68 | 64 | Qwen3.5 0.8B Q4_0 | `balanced` | adaptive |
| Capable 5–6 GB | 1.35 GB+ | 39–76 | 64 | Qwen2.5 1.5B Q4_K_M | `balanced` / `performance` | adaptive or cascade |
| Capable 6–8 GB | 1.55 GB+ | 45–86 | 64 | Qwen3 1.7B Q4_K_M | `performance` | adjacent fusion |
| Strong 8–12 GB | 3.0 GB+ | 66–95 | 64 | Qwen3 4B Q4_K_M | `performance` / `flagship` | guarded fusion |
| 12 GB+ | 5.7 GB+ | 82–100 | 64 | Qwen3 8B Q4_K_M | `flagship` | guarded fusion |

## Dynamic safeguards

- Normal model selection starts at 0.6B; 135M is an emergency fallback.
- Available RAM and thermal state are rechecked before every GGUF call.
- Context, batch, output tokens, and threads shrink under pressure.
- At least one logical CPU core is left available to Android and Termux.
- Hybrid passes use adjacent tiers sequentially; two GGUF processes are never resident together.
- Parameter counts are not added together.
- A valid first answer is preserved when a second pass becomes unsafe.
- Unknown processors are benchmarked rather than rejected by name.

## Flagship profile

Phones with approximately 9 GB or more usable total RAM, at least 3.8 GB live free RAM, and a high local CPU score can enter `flagship`. Temperature, battery, storage, memory pressure, and the remaining deadline can still force a smaller model, shorter context, fewer threads, or a single-pass answer.
