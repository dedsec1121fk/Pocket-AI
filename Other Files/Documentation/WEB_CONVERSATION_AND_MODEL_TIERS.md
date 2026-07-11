# Pocket AI 10: Web Intelligence, Follow-up Conversation, and Model Tiers

## Conversation continuity

Pocket AI restores recent persisted turns when it starts, keeps a bounded in-memory user/assistant transcript, resolves referential follow-ups, and passes the most recent turns to GGUF models in ChatML form. “Why?”, “make it simpler”, “another example”, “what about that?”, and equivalent Greek phrases therefore continue the active subject.

## Web modes

- `off`: no automatic web requests.
- `auto`: current-sensitive or explicitly online requests use web evidence.
- `on`: suitable knowledge requests use web evidence by default.
- `/search`: transient public search.
- `/web-learn`: reads permitted public pages and saves chunks to local SQLite retrieval memory.
- `/sources`: shows the previous source list.

Saved web learning is retrieval-augmented knowledge. It does not alter GGUF weights, cannot guarantee that a page is correct, and should not be treated as a substitute for authoritative verification in high-stakes situations.

## Intelligence tiers

- `fast`: bundled SmolLM2 135M Q2_K emergency tier.
- `quality`: bundled SmolLM2 135M Q4_1 emergency tier.
- `smart`: optional Qwen3 0.6B Q8_0.
- `ultra`: optional Qwen3 1.7B Q4_K_M.
- `pro`: optional Qwen3 4B Q4_K_M.
- `max`: optional Qwen3 8B Q4_K_M.

The 135M models cannot genuinely match ChatGPT 3.5. Their output is strengthened by deterministic tools, bilingual retrieval, the school database, evidence synthesis, validation, repair, persistent conversation, and optional web grounding. Larger tiers improve language understanding and reasoning when hardware allows. Automatic routing checks architecture, RAM, free RAM, CPU score, free storage, and temperature before selecting a tier.

## Time plan

Automatic web grounding uses short provider/page timeouts and normally reads at most one page before generation. Local generation still follows the shared 112-second inference budget. Explicit `/search` and `/web-learn` operations may take additional time because they are user-requested network tasks.
