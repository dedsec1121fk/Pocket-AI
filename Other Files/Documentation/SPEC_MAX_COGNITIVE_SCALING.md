# Spec-Max Cognitive Scaling

Pocket AI 14.0 applies a different reasoning and resource policy to every installed model instead of treating all models as interchangeable. It does **not** claim that a 135M model becomes GPT-3.5. The goal is the closest useful behaviour that each model and phone can safely sustain.

## What changed

- **Fast — SmolLM2 135M Q2_K:** acts as a precise evidence extractor. It receives a compact grounded draft, two-step instructions, low-variance sampling, and a strict output budget.
- **Quality — SmolLM2 135M Q4_1:** uses a three-step intent/evidence/verification pass and can participate in sequential bundled-model fusion on entry-class phones.
- **Smart — Qwen3 0.6B Q8_0:** receives larger context, four-step constraint and assumption checking, and task-specific verification.
- **Ultra — Qwen3 1.7B Q4_K_M:** performs conflict resolution, failure-mode analysis, and stronger code/calculation checking.
- **Pro — Qwen3 4B Q4_K_M:** uses deeper decomposition, alternatives, counterexamples, and guarded final verification.
- **Max — Qwen3 8B Q4_K_M:** uses the fullest local reasoning policy that still fits the shared deadline and live phone envelope.

## Hardware scaling

Six runtime profiles now cover ultra-eco, eco, entry, balanced, performance, and flagship phones. Flagship mode may use up to six inference threads while leaving at least one logical CPU core available to Android. Context and output ceilings expand only when free RAM, CPU score, temperature, battery state, storage, and remaining time allow it.

## Intelligence outside the GGUF weights

All tiers share 12,842 bilingual maximum-knowledge entries, 78,509 aliases, exact local tools, persistent retrieval, trusted web learning, advanced evidence ranking, and a 771-topic / 3,994-lesson school foundation. Stronger models can create compact high-confidence local lessons for smaller models.

## Safety and honesty

Pocket AI never disables Android thermal protection, never overclocks, never keeps two GGUF models resident simultaneously, and never treats fluent wording as proof. Current or high-stakes claims still require current authoritative sources.
