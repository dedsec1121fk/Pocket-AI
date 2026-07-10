# Pocket AI split GGUF package

The two SmolLM2 GGUF models are stored as ordered binary parts so every packaged model file stays below 60 MB.

## Included models

- `SmolLM2-135M-Instruct.Q2_K.gguf`: `part001` + `part002`
- `SmolLM2-135M-Instruct.Q4_1.gguf`: `part001` + `part002`

Each first part is 48 MiB. The remaining parts are smaller. Exact sizes and SHA-256 hashes are recorded in `split_models_manifest.json`.

Pocket AI automatically reconstructs the selected model into `Other Files/Saved Data/GGUF Models/` before llama.cpp inference. `Other Files/install_models.sh` can reconstruct and verify both models in advance.

Do not rename, edit, reorder, or separately decompress the part files. The reconstructed runtime files can be deleted safely; Pocket AI recreates them from these verified parts.
