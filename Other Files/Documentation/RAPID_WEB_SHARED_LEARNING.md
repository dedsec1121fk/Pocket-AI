# Rapid Web Shared Learning

Pocket AI 15.0 uses retrieval-based learning, not uncontrolled on-device weight training.

## Fast path

1. DDGS, Bing RSS, and Wikipedia are queried concurrently.
2. Results are deduplicated and ranked by query overlap and source trust.
3. Up to three readable public pages are fetched concurrently.
4. Evidence is summarized and inserted into SQLite in a single transaction per source.
5. Repeated searches and pages use bounded local caches.

## Shared model teaching

High-confidence stable answers are stored in `shared_model_learning.sqlite3`. The lesson records include the question, compact answer, evidence, source list, teacher model, confidence, and model-strength score. Every model tier can retrieve these lessons. Stronger lessons replace weaker duplicates.

Current-sensitive answers are never saved as timeless shared lessons. Web evidence remains source-labelled and current questions trigger fresh search.

## Limits

This architecture improves grounding, continuity, and reuse. It does not transform a 135M model into a large cloud model and does not modify GGUF weights.
