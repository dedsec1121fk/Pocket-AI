# Offline Encyclopedia Knowledge Provenance

Pocket AI includes a searchable offline encyclopedia index built from the first 50 approximately 1 MiB files in the public repository `ffatty/plain-text-wikipedia-simpleenglish`.

The repository describes the material as a plain-text Simple English Wikipedia corpus ported from the publisher's Kaggle dataset. Pocket AI retrieved and transformed the source files on **2026-07-09**.

## Packaged transformation

- 50 source text files
- 45,591 detected article records
- 68,342 searchable passages
- 51,087,206 indexed text characters
- 5 immutable SQLite FTS5 shards
- Largest encyclopedia shard: approximately 20.9 MiB
- Exact-title retrieval plus full-text relevance search
- Only short relevant passages are inserted into an LLM prompt

The source text files are not loaded into RAM and are not retained separately in the package. The SQLite indexes preserve article titles, passage text, source-file identifiers, and passage order.

## Important limitations

- This is an **offline, partial snapshot**, not the live encyclopedia.
- It may contain outdated, incomplete, simplified, disputed, or incorrect information.
- Current office-holders, laws, prices, software releases, medical guidance, security advisories, and other time-sensitive facts must be verified with current authoritative sources.
- Article-boundary detection is automatic; unusual source formatting can occasionally create imperfect titles or passage grouping.
- Pocket AI labels the retrieved material as offline encyclopedia evidence and instructs the model not to treat it as current authority.

## Attribution and licensing notice

Simple English Wikipedia states that its text is available under Creative Commons Attribution-ShareAlike and the GNU Free Documentation License, with additional terms potentially applying. Attribution and share-alike obligations remain applicable to redistributed or adapted Wikipedia text.

Source repository: `https://huggingface.co/ffatty/plain-text-wikipedia-simpleenglish`

Simple English Wikipedia: `https://simple.wikipedia.org/`

This package does not claim copyright over Wikipedia contributors' text. See `Other Files/Licenses/Simple-English-Wikipedia-Attribution.txt` for the bundled notice.
