# Pocket AI Emergency GGUF Parts

The two bundled SmolLM2 135M models are stored as ordered binary parts so every packaged model file remains below 60 MB.

These are **emergency fallbacks**, not Pocket AI 15's normal starting tier. Normal model selection begins with Qwen3 0.6B after the installer downloads a safe regular tier.

- `SmolLM2-135M-Instruct.Q2_K.gguf`: `part001` + `part002` → `emergency_fast`
- `SmolLM2-135M-Instruct.Q4_1.gguf`: `part001` + `part002` → `emergency_quality`

`Other Files/install_models.sh` reconstructs and verifies both models. The split manifest records exact part sizes, hashes, complete-model hashes, and their emergency role.
