# Lexical Knowledge Provenance

Pocket AI's lexical layer is a read-only transformation of two redistributable lexical resources:

1. **Princeton WordNet 3.0** — English nouns, verbs, adjectives, and adverbs grouped into synsets with definitions and semantic relations.
2. **Greek WordNet from Open Multilingual Wordnet** — Greek lemmas linked to Princeton WordNet 3.0 synset identifiers.

## Packaged transformation

- 117,659 English WordNet concepts
- 206,978 English lemma records
- 17,891 concepts with Greek links
- 23,853 Greek lemma records
- 7 SQLite FTS5 shards, each below 60 MB
- Exact lookup, morphology, definition search, synonyms, antonyms, and broader/narrower concept relations

The SQLite files are an indexing transformation for fast offline retrieval. They do not claim ownership over the source lexical content.

## Licenses and attribution

- The Princeton WordNet 3.0 license is included as `Other Files/Licenses/WordNet-3.0-License.txt`.
- The Greek WordNet/Open Multilingual Wordnet license notice used for this build is included as `Other Files/Licenses/Greek-WordNet-Apache-License.txt`.
- Source project pages: `https://wordnet.princeton.edu/` and `https://omwn.org/`.

Lexical data can contain uncommon, technical, historical, or imperfect senses. Pocket AI reranks common senses but users should still verify high-stakes interpretations.
