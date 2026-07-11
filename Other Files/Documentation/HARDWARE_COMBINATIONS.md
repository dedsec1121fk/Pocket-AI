# Pocket AI 16.0 Hardware Combination Matrix

These are conservative routing envelopes, not guarantees. Pocket AI rechecks live available RAM and temperature before every model pass.

| Approximate total RAM | Typical normal tier | Higher tier when live memory is strong |
|---:|---|---|
| 3–4 GB | 0.6B / 0.8B | 1.5B briefly |
| 5–6 GB | 1.5B / 1.7B | 2B |
| 7–8 GB | 2B | 3.09B Q3_K_M |
| 9–12 GB | 3.09B Q4_K_M / 4B | 8B only with ample free RAM |

Galaxy A22 variants are routed by live memory: 4 GB normally 0.6B–0.8B, 6 GB normally 1.5B–2B, and 8 GB can use 2B or 3.09B with guarded context.
