# Pocket AI 16 Runtime Modules

The runtime modules provide bilingual retrieval, conversation handling, exact tools, model-specific cognitive profiles, thermal/resource governance, web intelligence, and sequential hybrid orchestration.

`hybrid_orchestrator.py` routes the extended ladder `0.6B→0.8B→1.5B→1.7B→2B→3.09B`, with optional 4B/8B and emergency 135M fallbacks. It never loads two GGUF models simultaneously and never adds hybrid parameter counts.
