# Pocket AI Changelog

## Direct Chat + Simple Help Edition

- Removed the launcher from normal startup.
- Pocket AI now opens directly at the `You:` / `Εσύ:` chat prompt.
- Typing `help`, `/help`, `βοήθεια`, or `/βοήθεια` opens a simple numbered menu.
- Added natural phrases such as `scan my phone`, `find best model`, `change your name`, and `exit`.
- Added menu-driven teaching, file learning, safe web research, phone scanning, model status, and persona setup.
- Added a compact bilingual common-knowledge layer for reliable everyday definitions even when llama.cpp is not installed.
- Kept automatic phone scanning and resource-aware model selection in the background.
- Reduced technical startup output so the program waits for a normal question.

## Human Persona + Expanded Hybrid Edition

- Added main-menu option **Name & Humanize AI**.
- Added persistent AI name, optional user name, five conversation styles, and a natural-wording switch.
- Added `/persona`, `/name`, `/style`, and `/human` with Greek aliases.
- Added `adaptive`, `expert`, and `consensus` hybrid modes.
- Added a sequential consensus engine that compares independent Fast and Quality answers.
- Added prompt-context optimization for documents, memories, and recent conversation.
- Added route-aware answer confidence calibration.
- Added a resource-selection explanation module.
- Expanded hybrid control files from four to nine.
- Added a full GitHub-ready English/Greek `README.md`.
- Preserved all models, classifiers, specialists, licenses, saved-data separation, and no-root Termux support from the previous package.
