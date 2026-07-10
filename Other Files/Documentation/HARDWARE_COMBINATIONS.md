# Pocket AI Hardware Combination Matrix

Pocket AI measures live resources; advertised RAM alone is not sufficient. The rows below are representative safe starting points, not device guarantees.

| Total RAM | Free RAM | CPU score | Bitness | Recommended stack | Runtime | Hybrid |
|---:|---:|---:|:---:|---|---|---|
| 0.5-1 GB | 90-180 MB | 0-15 | 32/64 | Internal + Micro | ultra_eco | off |
| 1-1.5 GB | 150-280 MB | 5-20 | 32/64 | Internal + Lite | ultra_eco | off |
| 1.5-2 GB | 280-380 MB | 14-24 | 64 | Q2_K + Balanced | eco | speed |
| 2 GB | 380-520 MB | 24-35 | 64 | Q2_K + Balanced | entry | speed |
| 3 GB | 520-650 MB | 25-38 | 64 | Q2_K + Standard | entry | smart |
| 3 GB | 650-850 MB | 38-50 | 64 | Q4_1 + Standard | entry | smart |
| 4 GB | 820 MB-1.05 GB | 42-55 | 64 | Q4_1 + Max | balanced | adaptive |
| 4 GB | 1.05-1.3 GB | 55-70 | 64 | Q4_1 + Max | balanced | adaptive |
| 6 GB | 1.35-1.55 GB | 60-70 | 64 | Q4_1 + Max | performance | adaptive |
| 6 GB | 1.55-2 GB | 70-82 | 64 | Q2 draft → Q4 verify | performance | cascade |
| 8 GB+ | 2 GB+ | 82-100 | 64 | Q2/Q4 independent answers | performance | consensus |

## Dynamic safeguards

- Rechecks available RAM before every GGUF call.
- Reduces context, batch, tokens, and threads under memory pressure.
- Reduces threads and output length when the phone is hot.
- Uses one GGUF process at a time.
- Cancels the second hybrid pass if resources become unsafe.
- Uses the internal bilingual knowledge engine when 32-bit or critically constrained.
- Unknown processors are benchmarked instead of rejected by name.
