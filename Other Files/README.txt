Pocket AI — Expanded Automatic Model Matcher
=============================================

PACKAGE STRUCTURE
-----------------

Pocket AI.py
    Main program. Run this file from Termux.

Models/
    Contains all AI model data. No AI model is downloaded after extraction.

    GGUF language models:
      - SmolLM2-135M-Instruct.Q2_K.gguf
      - SmolLM2-135M-Instruct.Q4_1.gguf

    Pre-trained bilingual neural classifiers:
      - pretrained_micro/
      - pretrained_lite/
      - pretrained_balanced/
      - pretrained_standard/
      - pretrained_max/

    Bilingual generation models:
      - PocketAI_Bilingual_MicroLM_Lite.pkl.gz
      - PocketAI_Bilingual_MicroLM_Quality.pkl.gz

    Task-specialist models:
      - PocketAI_Code_Specialist.json.gz
      - PocketAI_Math_Specialist.json.gz
      - PocketAI_Research_Specialist.json.gz

Other Files/
    Contains documentation, licenses, checksums, the Termux llama.cpp builder,
    and Saved Data/. All files generated after launch remain under:

        Other Files/Saved Data/

MAIN MENU
---------

1. Scan Phone To Find Matching AI Model
2. Run Local AI

INSTALLATION
------------

    termux-setup-storage
    pkg update -y
    pkg install python unzip -y
    cd ~
    rm -rf "Pocket_AI"
    unzip -o ~/storage/downloads/Pocket_AI.zip -d ~/
    cd "~/Pocket_AI"
    chmod +x "Other Files/install_models.sh"
    "Other Files/install_models.sh"
    python "Pocket AI.py"

The installer verifies the bundled GGUF files and builds only the native
llama.cpp runner for the phone architecture. It does not download an AI model.

AUTOMATIC MODEL SELECTION
-------------------------

The scan measures CPU family, ABI, userspace bitness, cores, frequency, a short
benchmark, total RAM, available RAM, and free storage. It then selects:

  below about 0.9 GB or very low free RAM: Micro classifier + internal engine
  about 1-1.5 GB: Lite classifier + internal/Q2_K when safe
  about 1.5-2.4 GB: Balanced classifier + Q2_K
  about 2.4-3.6 GB: Standard classifier + Q2_K or Q4_1
  about 3.6 GB and above: MAX classifier + best compatible GGUF

The exact decision also depends on processor score, 64-bit support, currently
available RAM, storage, and whether each model passes its presence check.
Only one GGUF model is loaded at a time. One of five neural classifiers and one of two MicroLM variants are also selected automatically.

TASK ROUTING
------------

Coding, mathematics, and public-research questions activate their specialist
model automatically. The specialist may answer compact known questions itself
or provide a stricter task prompt to the selected GGUF model. English and Greek
remain the only supported languages.


MODEL CATALOG
-------------

Inside the chat, use:

    /models

Greek alias:

    /μοντέλα

This lists all twelve bundled model components, their file sizes, their state,
and the currently selected classifier, MicroLM, and GGUF model.
