# Pocket AI Maximum-Knowledge Architecture

Pocket AI uses retrieval-first intelligence so the smallest 135M model receives precise evidence instead of relying only on its limited parameters.

## Knowledge layers

| Layer | Packaged content | Purpose |
|---|---:|---|
| Curated bilingual database | 12,775 records, 78,149 aliases, 51 categories | High-confidence school, computing, science, mathematics, geography, and everyday facts |
| WordNet lexical graph | 117,659 concepts; 206,978 English lemmas | Definitions, senses, synonyms, antonyms, semantic relations |
| Greek lexical links | 17,891 linked concepts; 23,853 Greek lemmas | Greek concept matching and bilingual evidence |
| Offline encyclopedia | 45,591 articles; 68,342 passages; 51,087,206 characters | Broad people, places, history, science, culture, and general-reference evidence |
| User knowledge | Taught Q&A, memories, indexed documents, safe public research | Personal and project-specific expansion |

## Fast response path

1. Detect English or Greek.
2. Resolve exact tools and deterministic school mathematics.
3. Check curated exact aliases and high-confidence answers.
4. Use conservative direct encyclopedia extracts for exact, non-current English topics.
5. Search immutable SQLite FTS5 shards only when needed.
6. Rerank curated, encyclopedia, and lexical evidence for the exact query.
7. Compress the evidence to fit the active phone's context window.
8. Let the selected GGUF model generate one answer under a shared deadline.
9. On capable phones only, use a second independent/checking pass if time remains.
10. Cache only safe, high-confidence static results.

## Small-model strategy

The Q2_K model is treated as an evidence synthesizer rather than an encyclopedia stored entirely in weights. Its prompt receives:

- the most relevant curated facts first;
- short encyclopedia passages with article titles;
- lexical definitions only when useful;
- user memories and local-document evidence when relevant;
- explicit rules to distinguish evidence from inference and not invent sources, dates, commands, or security claims.

Low-end profiles use one generation pass. Balanced and performance profiles may use a second checking pass, but all local inference calls share the same global time plan.

## Time and memory controls

- Maximum local-inference plan: **112 seconds**
- Individual subprocess ceiling: **106 seconds**
- Remaining time is recalculated before every optional pass.
- Retrieval normally completes in a fraction of a second.
- Context, output tokens, batch size, micro-batch, and threads are reduced when RAM or temperature becomes unsafe.
- Only one GGUF process runs at a time.
- Every packaged model or knowledge shard remains below 60 MB.

The two-minute objective applies to Pocket AI's inference plan after startup. Very slow storage, first-run model reconstruction, Android process scheduling, thermal throttling, or external `llama.cpp` behavior can add overhead, so a universal wall-clock guarantee is not possible.
