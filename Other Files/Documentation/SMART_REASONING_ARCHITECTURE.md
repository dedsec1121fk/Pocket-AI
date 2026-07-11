# Pocket AI Smart Reasoning Architecture

## Objective

Pocket AI cannot make a 135M model intrinsically equivalent to a modern cloud model. It instead maximizes useful answer quality through deterministic tools, broad local retrieval, evidence compression, guarded generation, and post-generation validation.

## Answer pipeline

1. Classify the task: fact, explanation, comparison, procedure, coding, mathematics, summary, translation, recommendation, or creative writing.
2. Generate compact query variants and search curated bilingual knowledge, school knowledge, WordNet, offline encyclopedia shards, learned Q&A, user documents, memories, and specialists.
3. Rerank individual sentences rather than copying whole documents.
4. Build an evidence packet sized for the active model and phone.
5. Use exact deterministic tools when they are more reliable than generation.
6. Ask one local model to synthesize the answer. A second verification pass is used only when there is enough RAM, time, and thermal headroom.
7. Reject malformed, irrelevant, repetitive, unsupported, wrong-language, or obviously unsafe output and fall back to extractive evidence.

## Model tiers

- `fast`: SmolLM2 135M Q2_K, minimum memory.
- `quality`: SmolLM2 135M Q4_1, stronger bundled fallback.
- `smart`: Qwen3 0.6B Q8_0, recommended optional model.
- `ultra`: Qwen3 1.7B Q4_K_M, strongest optional model.

Only one GGUF process is loaded at a time. Automatic routing uses live RAM, CPU score, architecture, storage, temperature, battery state, question complexity, and remaining deadline.

## Time boundary

The generation plan shares a 112-second budget. This is a safety target for the Pocket AI inference process, not an unconditional device-independent promise. First-run downloads, model reconstruction, compilation, Android scheduling, and severe thermal throttling are outside the generation budget.

## Bilingual and comparison safeguards

- Greek school, science, computing, and networking concepts are bridged to English encyclopedia terms for retrieval, while answer generation is instructed to remain Greek.
- Comparison queries are split into their entities and the evidence packet reserves coverage for both sides.
- High-value stable comparisons and explanations use reviewed deterministic bilingual responses before a tiny model is allowed to improvise.
- If generation fails, Pocket AI returns the strongest relevant evidence instead of an unrelated fluent answer.


## Advanced deterministic reasoning

`advanced_reasoning.py` sits between retrieval and generation. It creates a task plan, enforces two-sided evidence for comparisons, solves supported exact tasks without hallucination, generates a grounded fallback, and audits model output for relevance, language, missing entities, unsupported precision, truncation, and prompt leakage. The generated answer is kept only when it passes the audit; otherwise Pocket AI repairs or replaces it with the evidence-grounded candidate.

## Qwen3 thinking policy

Routine and low-resource requests use `/no_think`. Difficult analysis can use `/think` only on safe balanced/performance profiles and while the shared inference deadline has enough time. Hidden reasoning tags are removed before display.

## Final critic gate

A short third pass is available only for difficult Qwen3 tasks when quality, deadline, RAM, and thermal gates all pass. It never runs on hot or critical devices and never loads a second model simultaneously.
