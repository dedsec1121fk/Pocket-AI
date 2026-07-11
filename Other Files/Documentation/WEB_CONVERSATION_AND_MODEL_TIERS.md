# Pocket AI 15: Web Intelligence, Follow-up Conversation, and Model Tiers

## Conversation continuity

Pocket AI restores recent persisted turns, keeps a bounded local transcript, resolves referential follow-ups, and passes only the most useful recent context to the selected GGUF model. Requests such as “Why?”, “make it simpler”, “another example”, and equivalent Greek phrases continue the active subject.

## Web modes

- `off`: no automatic web requests.
- `auto`: current-sensitive or explicitly online requests use web evidence.
- `on`: suitable knowledge requests use web evidence by default.
- `/search`: transient public search.
- `/web-learn`: reads permitted public pages and stores source-aware chunks in local SQLite retrieval memory.
- `/sources`: displays the previous source list.

Saved web learning is retrieval-augmented knowledge. It does not retrain GGUF weights and does not turn current information into guaranteed timeless truth.

## Intelligence tiers

- `emergency_fast`: bundled SmolLM2 135M Q2_K; emergency only.
- `emergency_quality`: bundled SmolLM2 135M Q4_1; emergency only.
- `fast`: Qwen3 0.6B Q8_0; normal minimum.
- `quality`: Qwen3.5 0.8B Q4_0.
- `smart`: Qwen2.5 1.5B Instruct Q4_K_M.
- `ultra`: Qwen3 1.7B Q4_K_M.
- `pro`: optional Qwen3 4B Q4_K_M.
- `max`: optional Qwen3 8B Q4_K_M.

Automatic routing checks architecture, total and free RAM, CPU score, free storage, battery, temperature, measured model behaviour, task complexity, and remaining time.

## Hybrid meaning

A hybrid is a sequential workflow between adjacent installed tiers. For example, `fast → quality` means a 0.6B analyst followed by a separate 0.8B synthesizer after the first model is unloaded. It does not create a 1.4B model, and parameter counts are never added.

## Time plan

Automatic web grounding uses bounded provider and page timeouts. Local generation follows the shared 112-second inference budget. Explicit `/search` and `/web-learn` operations may take longer because they are direct network tasks requested by the user.
