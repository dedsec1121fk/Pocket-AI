Pocket AI creates and updates its local runtime data in this folder.

Typical generated files:
  device_profile.json       hardware scan and automatic model match
  persona.json              AI name, user name, style, and natural wording
  dataset.json              bilingual intent training data
  neural_model.pkl.gz       selected local classifier
  model_metadata.json       classifier metadata
  knowledge.sqlite3         memories, learned Q&A, documents, and history
  language_model.pkl.gz     active bilingual MicroLM copy
  backups/                  local compressed backups
  llama.cpp/                locally compiled GGUF runner

Deleting generated files may reset learned knowledge or settings. The bundled
models under ../../Models/ are separate and should not be deleted during a data
reset.
