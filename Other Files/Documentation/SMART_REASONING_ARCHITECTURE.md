# Pocket AI 15 Smart Reasoning Architecture

## Objective

Pocket AI does not treat parameter count as the only source of intelligence. It combines real compact models with deterministic tools, broad local retrieval, evidence compression, guarded generation, shared verified lessons, and post-generation validation. It does not claim that a 135M or other small local model literally becomes GPT-3.5.

## Answer pipeline

1. Classify the task and identify entities, constraints, language, freshness, and risk.
2. Search the shared bilingual knowledge, school knowledge, WordNet, encyclopedia shards, learned Q&A, user documents, memories, and specialists.
3. Rerank individual evidence passages and compress them for the selected model.
4. Use deterministic tools when they are more reliable than language generation.
5. Select the strongest installed model that fits live RAM, CPU, storage, temperature, battery, and deadline constraints.
6. Run one model. For difficult work, run an immediately smaller adjacent analyst first, unload it, recheck safety, then run the stronger synthesizer.
7. Audit relevance, evidence support, completeness, language, code, calculations, truncation, and prompt leakage. Repair or fall back to grounded evidence when needed.

## Model tiers

- `emergency_fast`: SmolLM2 135M Q2_K; emergency only.
- `emergency_quality`: SmolLM2 135M Q4_1; emergency only.
- `fast`: Qwen3 0.6B Q8_0; normal minimum.
- `quality`: Qwen3.5 0.8B Q4_0.
- `smart`: Qwen2.5 1.5B Instruct Q4_K_M.
- `ultra`: Qwen3 1.7B Q4_K_M.
- `pro`: Qwen3 4B Q4_K_M.
- `max`: Qwen3 8B Q4_K_M.

Only one GGUF process is resident at a time. Hybrid parameter counts are not additive.

## Time and safety boundary

The local generation plan shares a 112-second budget. First-run downloads, model reconstruction, compilation, Android scheduling, and severe thermal throttling are outside that generation budget. Pocket AI can shorten context or output, reduce threads, skip a second pass, downgrade the model, or use retrieval-only fallback.

## Model-family policies

Qwen3 routine requests use non-thinking mode. Guarded thinking is available only for difficult Qwen3 tasks when live resources and the deadline permit it. Qwen2.5 and Qwen3.5 receive their own instruction formats and verification policies rather than Qwen3-only control tokens.

## Bilingual and exactness safeguards

- Greek requests may use English bridge terms for retrieval, while the final answer remains Greek.
- Comparisons reserve evidence for every entity.
- Mathematics, conversions, statistics, and supported equations prefer exact tools.
- Coding answers are checked for syntax, dependencies, paths, and likely runtime errors.
- Unsupported fluent output is replaced with the strongest grounded candidate.
