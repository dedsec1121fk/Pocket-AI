# Pocket AI advanced reasoning architecture

## Objective

Maximize answer correctness and usefulness on Android without pretending that a 135M model has cloud-scale capability. The system moves work from probabilistic generation into retrieval, exact tools, controlled planning, evidence coverage, and post-generation auditing.

## Pipeline

1. Detect language and task type.
2. Extract entities, constraints, requested format, and comparison sides.
3. Run deterministic tools for supported arithmetic, percentages, equations, statistics, number bases, prime/GCD/LCM/factorial, and exact character counts.
4. Retrieve curated bilingual knowledge, encyclopedia passages, WordNet, memories, learned documents, and specialist evidence.
5. Score evidence with source priors, lexical overlap, entity coverage, and redundancy penalties.
6. Build a compact reasoning blueprint and deterministic grounded candidate.
7. Select the strongest safe installed model from the live RAM/CPU/thermal matrix.
8. Use Qwen3 non-thinking mode for routine work; allow guarded thinking only for complex work on capable hardware.
9. Audit the answer for language, task coverage, missing comparison entities, unsupported precision, prompt leakage, truncation, and relevance.
10. Keep, repair, or replace the model output with the grounded candidate.

## Deadline policy

All local generation shares a 112-second inference plan. Retrieval and exact tools are normally sub-second. Multi-pass reasoning is disabled or reduced when live resources or remaining time are insufficient.

## Capability boundary

The 135M models are emergency natural-language renderers. They cannot become equivalent to a modern cloud model. Their effective accuracy improves because exact and factual work is performed outside the model. The normal ladder spans 0.6B, 0.8B, 1.5B, 1.7B, 2B, and 3.09B, with optional 4B/8B tiers for devices that can run them safely.
