#!/usr/bin/env python3
"""
PocketAI BILINGUAL MAX
======================
A substantial English-and-Greek-only offline AI assistant for low-end Android phones running Termux.

Everything is implemented with Python's standard library:
- Unicode tokenizer and stable feature hashing
- Sparse two-hidden-layer neural intent classifier
- Backpropagation, training, validation, early stopping, and compressed models
- Persistent SQLite retrieval memory for questions, answers, notes, and documents
- Local document ingestion with an inverted term index
- Safe calculator and useful offline utilities
- Strict English/Greek language routing and bilingual response generation
- Persistent user memories and conversation history
- Bundled bilingual MicroLM generator
- Safe public-web research using constrained search operators
- Optional SmolLM2 135M GGUF reasoning through llama.cpp
- Automatic RAM-aware model profiles

No root, TensorFlow, PyTorch, NumPy, or cloud API is needed. Core use remains offline; /dork and /web-learn use the public internet only when explicitly requested.

Examples:
    python "Pocket AI.py"
    python "Pocket AI.py" --train
    python "Pocket AI.py" --profile max --train
    python "Pocket AI.py" --benchmark
    python "Pocket AI.py" --data ~/PocketAI_Bilingual_MAX

The default "auto" profile chooses a practical network size from available RAM.
Use --profile extreme only when you accept slower first-run training.
"""

from __future__ import annotations

import argparse
import ast
import csv
import datetime as _dt
import difflib
import gzip
import hashlib
import html
import ipaddress
import json
import math
import operator
import os
import platform
import pickle
import random
import re
import shutil
import socket
import sqlite3
import statistics
import subprocess
import sys
import tarfile
import textwrap
import time
import traceback
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET
import zlib
from array import array
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Deque, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple


APP_NAME = "PocketAI Bilingual MAX"
MODEL_VERSION = 7
DATASET_VERSION = 6
RANDOM_SEED = 1121
DEFAULT_CONFIDENCE = 0.42
MAX_INPUT_CHARS = 4000
MAX_FILE_BYTES = 6 * 1024 * 1024
MAX_INGEST_FILES = 300
MAX_DOCUMENT_CHUNKS_PER_FILE = 1200
HISTORY_LIMIT = 60
WEB_USER_AGENT = "PocketAI-WebResearch/1.0 (+local educational research)"
WEB_SEARCH_TIMEOUT = 14
WEB_PAGE_TIMEOUT = 12
WEB_MAX_DOWNLOAD_BYTES = 700 * 1024
WEB_MAX_RESULTS = 8
WEB_MAX_PAGES_PER_RUN = 4
WEB_DELAY_SECONDS = 1.0
EXTERNAL_LLM_MODELS = {
    "fast": {
        "filename": "SmolLM2-135M-Instruct.Q2_K.gguf",
        "sha256": "1e014d3c45f6cf502397a3b85b1d9d282605afb02079fd32665b0422c3f0106c",
        "label": "SmolLM2 135M Q2_K (fast / minimum RAM)",
        "context": 768,
        "batch": 64,
        "max_tokens": 176,
    },
    "quality": {
        "filename": "SmolLM2-135M-Instruct.Q4_1.gguf",
        "sha256": "b179c9523d0e6a0f98a330c7562b682750a6f8c8c15e5bc70ea373728110db53",
        "label": "SmolLM2 135M Q4_1 (higher quality)",
        "context": 1024,
        "batch": 64,
        "max_tokens": 224,
    },
}
DEFAULT_EXTERNAL_LLM_MODEL = "fast"

LLM_CPU_PROFILES = {
    "ultra_eco": {
        "threads": 1,
        "context": {"fast": 256, "quality": 256},
        "batch": 8,
        "ubatch": 8,
        "max_tokens": {"fast": 56, "quality": 64},
        "timeout": 420,
        "description": "Emergency profile for very low free RAM, 32-bit userspace, or extremely slow processors.",
    },
    "eco": {
        "threads": 1,
        "context": {"fast": 384, "quality": 384},
        "batch": 16,
        "ubatch": 8,
        "max_tokens": {"fast": 80, "quality": 88},
        "timeout": 360,
        "description": "Minimum-memory profile for roughly 1.5-2 GB devices and heavily throttled processors.",
    },
    "entry": {
        "threads": 2,
        "context": {"fast": 512, "quality": 512},
        "batch": 32,
        "ubatch": 16,
        "max_tokens": {"fast": 112, "quality": 128},
        "timeout": 300,
        "description": "Entry-level profile for Cortex-A53/A55 phones such as Galaxy A12-class devices.",
    },
    "balanced": {
        "threads": 3,
        "context": {"fast": 640, "quality": 768},
        "batch": 48,
        "ubatch": 32,
        "max_tokens": {"fast": 144, "quality": 176},
        "timeout": 240,
        "description": "Balanced profile for mainstream 3-4 GB phones and efficient mid-range processors.",
    },
    "performance": {
        "threads": 4,
        "context": {"fast": 768, "quality": 1024},
        "batch": 64,
        "ubatch": 48,
        "max_tokens": {"fast": 176, "quality": 224},
        "timeout": 180,
        "description": "Quality-first profile for modern mid-range and flagship processors with comfortable free RAM.",
    },
}
DEFAULT_LLM_CPU_PROFILE = "auto"

# Rules identify major Android-phone SoC families and many common model-number
# schemes. Unknown processors are still supported through architecture, core,
# frequency, RAM, storage, and a short local benchmark rather than a name-only
# lookup. The priority order matters: specific/high-end rules come first.
PROCESSOR_FAMILY_RULES = [
    # Google
    (r"tensor\s*g?5|gs501", "Google", "Tensor G5", 92),
    (r"tensor\s*g?4|zumapro", "Google", "Tensor G4", 88),
    (r"tensor\s*g?3|zuma", "Google", "Tensor G3", 84),
    (r"tensor\s*g?2|gs201", "Google", "Tensor G2", 78),
    (r"\btensor\b|gs101", "Google", "Tensor G1", 72),

    # Qualcomm Snapdragon and internal SM/MSM/APQ identifiers
    (r"snapdragon\s*8\s*(elite|gen\s*[2345])|sm8(?:750|650|550|475|450)", "Qualcomm", "Snapdragon 8 flagship", 95),
    (r"snapdragon\s*8|sm8\d{3}|sdm8\d{2}", "Qualcomm", "Snapdragon 8 series", 88),
    (r"snapdragon\s*7\+?|sm7\d{3}|sdm7\d{2}", "Qualcomm", "Snapdragon 7 series", 72),
    (r"snapdragon\s*6|sm6\d{3}|sdm6\d{2}", "Qualcomm", "Snapdragon 6 series", 58),
    (r"snapdragon\s*4|sm4\d{3}|sdm4\d{2}", "Qualcomm", "Snapdragon 4 series", 43),
    (r"snapdragon\s*2|sm2\d{3}", "Qualcomm", "Snapdragon 2 series", 27),
    (r"msm8998|msm8996|msm8994|apq8096", "Qualcomm", "Older Snapdragon 8xx", 48),
    (r"msm8953|msm8956|msm8976|sdm63[026]|sdm66[06]", "Qualcomm", "Older Snapdragon 6xx", 38),
    (r"msm8937|msm8940|msm8917|msm8920|sdm4[235]0", "Qualcomm", "Older Snapdragon 4xx", 25),
    (r"qualcomm|qcom|msm\d+|apq\d+", "Qualcomm", "Snapdragon/Qualcomm", 42),

    # MediaTek Dimensity, Helio and MT identifiers
    (r"dimensity\s*(9\d{3}|9400|9300|9200)|mt69\d{2}", "MediaTek", "Dimensity 9000 series", 90),
    (r"dimensity\s*8\d{3}", "MediaTek", "Dimensity 8000 series", 80),
    (r"dimensity\s*7\d{3}", "MediaTek", "Dimensity 7000 series", 69),
    (r"dimensity\s*6\d{3}", "MediaTek", "Dimensity 6000 series", 58),
    (r"dimensity\s*1\d{3}", "MediaTek", "Dimensity 1000 series", 62),
    (r"dimensity\s*[789]\d{2}|mt68(?:99|95|83|78|77|73|53|33)", "MediaTek", "Dimensity mobile", 61),
    (r"helio\s*g(?:99|96|95|90)|mt6789|mt6785", "MediaTek", "Helio G9x", 49),
    (r"helio\s*g(?:88|85|80)|mt6769", "MediaTek", "Helio G8x", 42),
    (r"helio\s*g\d+", "MediaTek", "Helio G series", 37),
    (r"helio\s*p(?:95|90|70|65|60)|mt6779|mt6771", "MediaTek", "Helio P upper entry", 40),
    (r"helio\s*p35|mt6765", "MediaTek", "Helio P35", 24),
    (r"helio\s*p\d+|mt676[123]", "MediaTek", "Helio P series", 29),
    (r"helio\s*a\d+|mt6739|mt6761", "MediaTek", "Helio A series", 20),
    (r"mediatek|mtk|mt\d{4}", "MediaTek", "MediaTek mobile", 35),

    # Samsung Exynos / S5E identifiers
    (r"exynos\s*2500|s5e9955", "Samsung", "Exynos 2500", 91),
    (r"exynos\s*2400|s5e9945", "Samsung", "Exynos 2400", 87),
    (r"exynos\s*2200|s5e9925", "Samsung", "Exynos 2200", 80),
    (r"exynos\s*2100|s5e9840", "Samsung", "Exynos 2100", 75),
    (r"exynos\s*1[345]\d{2}|s5e88\d{2}", "Samsung", "Exynos 1xxx mid-range", 58),
    (r"exynos\s*9\d{3}|s5e98\d{2}", "Samsung", "Exynos 9 series", 59),
    (r"exynos\s*8\d{3}|s5e78\d{2}", "Samsung", "Exynos 8 series", 39),
    (r"exynos\s*850|s5e3830", "Samsung", "Exynos 850", 25),
    (r"exynos\s*7\d{3}|s5e7870|s5e7884|s5e7885", "Samsung", "Exynos 7 series", 25),
    (r"exynos|s5e\d+", "Samsung", "Exynos", 43),

    # Unisoc / Spreadtrum
    (r"unisoc\s*t9\d{2}|ums9620|t820", "Unisoc", "Unisoc T9/T8 series", 55),
    (r"unisoc\s*t7\d{2}|t6\d{2}|ums9230", "Unisoc", "Unisoc T7/T6 series", 43),
    (r"unisoc\s*t6(?:16|18)|ums512|ums312", "Unisoc", "Unisoc T6 entry", 31),
    (r"unisoc\s*t3\d{2}|unisoc\s*t2\d{2}|sc9863", "Unisoc", "Unisoc T3/T2 entry", 26),
    (r"sc9832|sc7731|spreadtrum", "Unisoc", "Spreadtrum legacy", 15),
    (r"unisoc|ums\d+|sc\d{4}", "Unisoc", "Unisoc mobile", 31),

    # Huawei HiSilicon Kirin
    (r"kirin\s*9\d{2}|hi36\d{2}", "HiSilicon", "Kirin 9 series", 68),
    (r"kirin\s*8\d{2}|hi62\d{2}", "HiSilicon", "Kirin 8 series", 50),
    (r"kirin\s*7\d{2}", "HiSilicon", "Kirin 7 series", 36),
    (r"kirin\s*6\d{2}", "HiSilicon", "Kirin 6 series", 24),
    (r"kirin|hisi|hisilicon|hi\d{4}", "HiSilicon", "Kirin/HiSilicon", 43),

    # Other Android mobile/tablet families
    (r"tegra\s*x1|tegra210", "NVIDIA", "Tegra X1", 45),
    (r"tegra|nvidia", "NVIDIA", "Tegra", 35),
    (r"rk3588", "Rockchip", "RK3588", 69),
    (r"rk356[68]", "Rockchip", "RK356x", 44),
    (r"rk3399", "Rockchip", "RK3399", 40),
    (r"rockchip|rk3\d{3}", "Rockchip", "Rockchip", 31),
    (r"allwinner\s*h6|sun50iw6", "Allwinner", "Allwinner H6", 31),
    (r"allwinner|sun\d+i", "Allwinner", "Allwinner", 23),
    (r"amlogic\s*s9\d{2}|meson", "Amlogic", "Amlogic", 29),
    (r"intel.*atom|atom.*z[2358]\d{3}|x86_64", "Intel", "Atom/x86 Android", 32),
]

AI_MODEL_COMPATIBILITY = {
    "internal": {
        "label": "PocketAI internal bilingual engine",
        "minimum_total_ram": 512 * 1024 ** 2,
        "minimum_available_ram": 90 * 1024 ** 2,
        "minimum_free_storage": 35 * 1024 ** 2,
        "minimum_cpu_score": 0,
        "requires_64_bit": False,
        "processor_combos": "Any Android processor able to run modern Termux/Python; used as the universal fallback.",
    },
    "fast": {
        "label": "SmolLM2-135M Q2_K Fast",
        "minimum_total_ram": 1450 * 1024 ** 2,
        "minimum_available_ram": 300 * 1024 ** 2,
        "minimum_free_storage": 170 * 1024 ** 2,
        "minimum_cpu_score": 14,
        "requires_64_bit": True,
        "processor_combos": "Entry-level or better 64-bit ARM/x86: Cortex-A53/A55, Snapdragon 2/4+, Helio A/P/G, Exynos 7/850+, Unisoc T/SC9863+, Kirin 6+, and newer.",
    },
    "quality": {
        "label": "SmolLM2-135M Q4_1 Quality",
        "minimum_total_ram": 2050 * 1024 ** 2,
        "minimum_available_ram": 560 * 1024 ** 2,
        "minimum_free_storage": 220 * 1024 ** 2,
        "minimum_cpu_score": 35,
        "requires_64_bit": True,
        "processor_combos": "Efficient entry/mid-range or better: Snapdragon 6/7/8, Dimensity, Helio G8x/G9x, Exynos 9/1xxx/2xxx, Tensor, Kirin 8/9, Unisoc T7/T8/T9, or similarly scoring processors.",
    },
}

WORD_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)?", re.UNICODE)
SENTENCE_RE = re.compile(r"(?<=[.!?;])\s+|\n{2,}")
HTML_TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")

SUPPORTED_TEXT_SUFFIXES = {
    ".txt", ".md", ".markdown", ".rst", ".log", ".csv", ".tsv",
    ".json", ".jsonl", ".xml", ".html", ".htm", ".py", ".sh",
    ".bash", ".zsh", ".js", ".ts", ".css", ".java", ".c", ".h",
    ".cpp", ".hpp", ".go", ".rs", ".ini", ".cfg", ".conf", ".yaml",
    ".yml", ".toml", ".sql"
}

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by",
    "can", "could", "did", "do", "does", "for", "from", "had", "has",
    "have", "he", "her", "here", "hers", "him", "his", "how", "i",
    "if", "in", "into", "is", "it", "its", "me", "more", "my", "no",
    "not", "of", "on", "or", "our", "ours", "she", "so", "some",
    "than", "that", "the", "their", "theirs", "them", "then", "there",
    "these", "they", "this", "those", "to", "too", "up", "us", "was",
    "we", "were", "what", "when", "where", "which", "who", "why",
    "will", "with", "would", "you", "your", "yours",
    "και", "να", "το", "τα", "τη", "την", "της", "του", "των", "σε",
    "στο", "στη", "στην", "για", "με", "μου", "σου", "είναι", "ειναι",
    "που", "πως", "πώς", "τι", "ένα", "μια", "ο", "η", "οι"
}

MODEL_PROFILES = {
    "micro": {
        "hash_size": 2048,
        "hidden1": 28,
        "hidden2": 12,
        "epochs": 58,
        "learning_rate": 0.041,
        "description": "Minimum neural profile for sub-1 GB and heavily constrained phones."
    },
    "lite": {
        "hash_size": 4096,
        "hidden1": 40,
        "hidden2": 16,
        "epochs": 72,
        "learning_rate": 0.036,
        "description": "Fast profile for roughly 1-2 GB RAM devices."
    },
    "balanced": {
        "hash_size": 8192,
        "hidden1": 52,
        "hidden2": 22,
        "epochs": 82,
        "learning_rate": 0.032,
        "description": "Balanced profile for older phones with around 2-3 GB RAM."
    },
    "standard": {
        "hash_size": 12288,
        "hidden1": 60,
        "hidden2": 26,
        "epochs": 92,
        "learning_rate": 0.030,
        "description": "Stronger middle profile for 3-4 GB phones without the MAX memory cost."
    },
    "max": {
        "hash_size": 24576,
        "hidden1": 72,
        "hidden2": 34,
        "epochs": 104,
        "learning_rate": 0.027,
        "description": "Large pre-trained classifier for capable phones selected by the hardware scanner."
    },
    "extreme": {
        "hash_size": 49152,
        "hidden1": 88,
        "hidden2": 42,
        "epochs": 124,
        "learning_rate": 0.024,
        "description": "Maximum-capacity classifier for high-memory devices; automatic mode normally uses the bundled max model."
    }
}


GREEK_CHAR_RE = re.compile(r"[\u0370-\u03ff\u1f00-\u1fff]")
LATIN_CHAR_RE = re.compile(r"[A-Za-z]")
OTHER_LETTER_RE = re.compile(r"[^\W\d_A-Za-z\u0370-\u03ff\u1f00-\u1fff]", re.UNICODE)

SUPPORTED_LANGUAGES = {"en", "el"}
LANGUAGE_NAMES = {"en": "English", "el": "Ελληνικά", "auto": "Automatic / Αυτόματα"}

# Canonical concept aliases improve paraphrase recognition and allow English and
# Greek wording to meet in the same retrieval space without an external model.
CONCEPT_ALIASES = {
    "internet": "concept_internet", "wifi": "concept_internet", "online": "concept_internet",
    "web": "concept_web", "search": "concept_web", "research": "concept_web", "dork": "concept_web", "dorking": "concept_web",
    "ιστος": "concept_web", "ιστο": "concept_web", "αναζητηση": "concept_web", "ερευνα": "concept_web",
    "llm": "concept_llm", "gguf": "concept_llm", "smollm": "concept_llm", "model": "concept_llm",
    "μοντελο": "concept_llm", "γλωσσικο": "concept_llm",
    "ιντερνετ": "concept_internet", "διαδικτυο": "concept_internet", "συνδεση": "concept_internet",
    "password": "concept_password", "passwords": "concept_password", "passphrase": "concept_password",
    "κωδικος": "concept_password", "κωδικοι": "concept_password", "συνθηματικο": "concept_password",
    "file": "concept_file", "files": "concept_file", "folder": "concept_file", "directory": "concept_file",
    "αρχειο": "concept_file", "αρχεια": "concept_file", "φακελος": "concept_file",
    "document": "concept_document", "documents": "concept_document", "notes": "concept_document",
    "εγγραφο": "concept_document", "εγγραφα": "concept_document", "σημειωσεις": "concept_document",
    "memory": "concept_memory", "remember": "concept_memory", "recall": "concept_memory",
    "μνημη": "concept_memory", "θυμησου": "concept_memory", "θυμασαι": "concept_memory",
    "train": "concept_training", "training": "concept_training", "retrain": "concept_training",
    "εκπαιδευση": "concept_training", "εκπαιδευσε": "concept_training", "μαθηση": "concept_training",
    "teach": "concept_teach", "learn": "concept_teach", "knowledge": "concept_teach", "information": "concept_teach", "info": "concept_teach", "add": "concept_teach",
    "μαθε": "concept_teach", "γνωση": "concept_teach", "διδαξε": "concept_teach", "πληροφορια": "concept_teach", "πληροφοριες": "concept_teach", "προσθεσω": "concept_teach", "προσθεσε": "concept_teach",
    "phone": "concept_phone", "android": "concept_phone", "mobile": "concept_phone",
    "κινητο": "concept_phone", "τηλεφωνο": "concept_phone",
    "battery": "concept_battery", "overheating": "concept_battery", "heat": "concept_battery", "hot": "concept_battery", "heating": "concept_battery",
    "μπαταρια": "concept_battery", "ζεστη": "concept_battery", "θερμοκρασια": "concept_battery", "καιει": "concept_battery", "ζεσταινεται": "concept_battery",
    "security": "concept_security", "secure": "concept_security", "cybersecurity": "concept_security", "protect": "concept_security", "protection": "concept_security",
    "ασφαλεια": "concept_security", "κυβερνοασφαλεια": "concept_security", "προστασια": "concept_security", "προστατευω": "concept_security", "προστατεψω": "concept_security",
    "phishing": "concept_phishing", "scam": "concept_phishing", "fraud": "concept_phishing",
    "απατη": "concept_phishing", "ψαρεμα": "concept_phishing", "υποπτο": "concept_phishing",
    "malware": "concept_malware", "virus": "concept_malware", "trojan": "concept_malware",
    "ιος": "concept_malware", "κακοβουλο": "concept_malware",
    "backup": "concept_backup", "restore": "concept_backup", "copy": "concept_backup", "copies": "concept_backup", "preserve": "concept_backup", "safely": "concept_backup",
    "αντιγραφο": "concept_backup", "αντιγραφα": "concept_backup", "επαναφορα": "concept_backup", "διατηρησω": "concept_backup",
    "code": "concept_code", "coding": "concept_code", "programming": "concept_code",
    "κωδικας": "concept_code", "προγραμματισμος": "concept_code",
    "error": "concept_error", "debug": "concept_error", "traceback": "concept_error", "exception": "concept_error", "crash": "concept_error", "failure": "concept_error",
    "σφαλμα": "concept_error", "λαθος": "concept_error", "αποσφαλματωση": "concept_error", "εξαιρεση": "concept_error", "κρασαρει": "concept_error",
    "weather": "concept_weather", "forecast": "concept_weather", "rain": "concept_weather",
    "καιρος": "concept_weather", "προγνωση": "concept_weather", "βροχη": "concept_weather",
    "news": "concept_news", "headlines": "concept_news", "events": "concept_news",
    "ειδησεις": "concept_news", "νεα": "concept_news", "γεγονοτα": "concept_news",
    "calculate": "concept_math", "calculator": "concept_math", "math": "concept_math",
    "υπολογισε": "concept_math", "αριθμομηχανη": "concept_math", "μαθηματικα": "concept_math",
    "ai": "concept_ai", "artificial": "concept_ai", "neural": "concept_ai",
    "τεχνητη": "concept_ai", "νοημοσυνη": "concept_ai", "νευρωνικο": "concept_ai",
    "limitation": "concept_limitations", "limitations": "concept_limitations", "unable": "concept_limitations", "cannot": "concept_limitations", "weakness": "concept_limitations",
    "περιορισμος": "concept_limitations", "περιορισμοι": "concept_limitations", "αδυναμια": "concept_limitations", "μπορεις": "concept_capability",
    "termux": "concept_termux", "terminal": "concept_termux", "shell": "concept_termux",
    "τερματικο": "concept_termux",
}

GREEK_RESPONSES = {
    "greeting": ["Γεια σου{name_suffix}. Είμαι έτοιμο.", "Καλησπέρα{name_suffix}. Τι θέλεις να κάνουμε;"],
    "goodbye": ["Αντίο{name_suffix}.", "Τα λέμε αργότερα."],
    "identity": ["Είμαι το PocketAI Bilingual MAX, ένας υβριδικός βοηθός που λειτουργεί τοπικά σε Python.", "Συνδυάζω νευρωνική ταξινόμηση, αναζήτηση γνώσης, μνήμη και τοπικά εργαλεία."],
    "capabilities": ["Μπορώ να ταξινομώ αιτήματα, να βρίσκω διδαγμένες απαντήσεις, να διαβάζω αρχεία, να θυμάμαι στοιχεία, να κάνω υπολογισμούς και να δουλεύω offline.", "Χρησιμοποίησε /βοήθεια για όλες τις εντολές. Η γνώση μου μεγαλώνει με /teach, /remember και /ingest."],
    "help": ["Γράψε /βοήθεια για να δεις όλες τις εντολές μάθησης, μνήμης, εγγράφων, εκπαίδευσης και συντήρησης."],
    "thanks": ["Παρακαλώ{name_suffix}.", "Χαίρομαι που βοήθησα."],
    "apology": ["Δεν υπάρχει πρόβλημα.", "Εντάξει, μπορούμε να συνεχίσουμε."],
    "status": ["Λειτουργώ κανονικά. Χρησιμοποίησε /stats για τεχνικές λεπτομέρειες.", "Το μοντέλο και η τοπική βάση γνώσης είναι έτοιμα."],
    "offline": ["Λειτουργώ offline αφού εγκατασταθεί η Python. Η επεξεργασία, η μνήμη και η αναζήτηση μένουν στη συσκευή.", "Δεν χρειάζομαι σύνδεση στο διαδίκτυο για τη συνηθισμένη λειτουργία μου."],
    "privacy": ["Το μοντέλο, οι μνήμες, τα έγγραφα και το ιστορικό αποθηκεύονται τοπικά στον φάκελο {data_dir}.", "Δεν ανεβάζω συνομιλίες σε cloud υπηρεσία. Προστάτευσε όμως τη συσκευή και τα τοπικά αρχεία."],
    "training": ["Ο νευρωνικός ταξινομητής εκπαιδεύεται από το dataset.json με backpropagation. Μετά από αλλαγές στα intents, εκτέλεσε /train.", "Για άμεση νέα γνώση χρησιμοποίησε /teach. Για αλλαγή συμπεριφοράς intents χρειάζεται επανεκπαίδευση."],
    "termux": ["Ο βοηθός είναι σχεδιασμένος για Python στο Termux και δεν χρειάζεται root.", "Αποφεύγει βαριά frameworks ώστε να λειτουργεί σε παλιότερα Android κινητά."],
    "android": ["Το Android μπορεί να τρέξει τοπική Python μέσω Termux. Η απόδοση εξαρτάται από RAM, θερμοκρασία και εφαρμογές παρασκηνίου.", "Για παλιό κινητό προτίμησε το max ή balanced profile ανάλογα με τη διαθέσιμη μνήμη."],
    "python": ["Η Python είναι γλώσσα προγραμματισμού γενικής χρήσης. Στο Termux εγκαθίσταται με pkg install python.", "Για σφάλμα Python δώσε ολόκληρο το traceback και τον σχετικό κώδικα."],
    "linux": ["Σε περιβάλλον Linux οι βασικές εντολές είναι ls, cd, cp, mv, pwd και chmod.", "Πρόσεχε καταστροφικές εντολές όπως rm -rf και έλεγχε πάντα τη διαδρομή."],
    "files": ["Στο Termux το ls εμφανίζει αρχεία, το cp αντιγράφει, το mv μετακινεί ή μετονομάζει και το rm διαγράφει.", "Τα Downloads είναι συνήθως διαθέσιμα ως ~/storage/downloads μετά το termux-setup-storage."],
    "storage": ["Εκτέλεσε df -h για τον διαθέσιμο χώρο. Το termux-setup-storage δημιουργεί συντομεύσεις προς την κοινόχρηστη αποθήκευση.", "Τα μεγάλα έγγραφα και τα backup καταναλώνουν περισσότερο χώρο από το ίδιο το μοντέλο."],
    "battery": ["Η εκπαίδευση χρησιμοποιεί έντονα τον επεξεργαστή. Κράτησε το κινητό δροσερό και χρησιμοποίησε μικρότερο profile αν ζεσταίνεται.", "Η απλή συνομιλία είναι ελαφριά, ενώ η εκπαίδευση και η εισαγωγή πολλών αρχείων καταναλώνουν περισσότερη μπαταρία."],
    "time": ["Η τοπική ώρα είναι {time}.", "Στη συσκευή είναι {time}."],
    "date": ["Η τοπική ημερομηνία είναι {date}.", "Σήμερα είναι {date}."],
    "weather": ["Δεν μπορώ να γνωρίζω τον ζωντανό καιρό ενώ λειτουργώ πλήρως offline. Η τρέχουσα πρόγνωση χρειάζεται εξωτερική πηγή δεδομένων.", "Μπορείς να εισαγάγεις αποθηκευμένες μετεωρολογικές σημειώσεις, αλλά όχι να λάβεις ζωντανή πρόγνωση χωρίς διαδίκτυο."],
    "news": ["Δεν μπορώ να επαληθεύσω τρέχουσες ειδήσεις χωρίς ενημερωμένη εξωτερική πηγή. Μπορείς να εισαγάγεις αποθηκευμένα άρθρα.", "Η ενσωματωμένη γνώση είναι στατική, επομένως τα σημερινά γεγονότα χρειάζονται νέα δεδομένα."],
    "calculator": ["Ξεκίνα το μήνυμα με = ή calc, για παράδειγμα: = (12 + 8) * 3.", "Διαθέτω ασφαλή offline αριθμομηχανή με αριθμητικές πράξεις και επιλεγμένες μαθηματικές συναρτήσεις."],
    "math": ["Δώσε συγκεκριμένη αριθμητική παράσταση μετά από =. Για συμβολικό πρόβλημα εξήγησε τις μεταβλητές και το ζητούμενο.", "Τα μαθηματικά γίνονται ευκολότερα όταν γράφουμε καθαρά τα γνωστά, τα άγνωστα και τους περιορισμούς."],
    "science": ["Η επιστημονική μέθοδος βασίζεται σε παρατήρηση, ελέγξιμες υποθέσεις, πείραμα, αποδείξεις και επαναληψιμότητα.", "Κάνε συγκεκριμένη επιστημονική ερώτηση ή εισήγαγε αξιόπιστες σημειώσεις για τοπική αναζήτηση."],
    "history": ["Ρώτησε για συγκεκριμένη εποχή, τόπο ή γεγονός. Για λεπτομερή ακρίβεια εισήγαγε ένα αξιόπιστο ιστορικό αρχείο.", "Η ιστορική ανάλυση πρέπει να ξεχωρίζει τις πρωτογενείς πηγές, τις μεταγενέστερες ερμηνείες και την αβεβαιότητα."],
    "geography": ["Κάνε συγκεκριμένη γεωγραφική ερώτηση. Στατικά στοιχεία μπορούν να προστεθούν με /teach ή /ingest.", "Η γεωγραφία μελετά το φυσικό περιβάλλον, τους πληθυσμούς, τα σύνορα, το κλίμα και τις χωρικές σχέσεις."],
    "study": ["Χρησιμοποίησε ενεργή ανάκληση, επανάληψη σε διαστήματα, σύντομες συνεδρίες συγκέντρωσης και ερωτήσεις εξάσκησης.", "Χώρισε το μάθημα σε μικρούς στόχους, εξέτασε τον εαυτό σου και επέστρεψε στα αδύναμα σημεία."],
    "motivation": ["Μείωσε την εργασία σε μία πράξη κάτω των πέντε λεπτών και ξεκίνησε πριν αξιολογήσεις το κίνητρό σου.", "Η πρόοδος είναι ευκολότερη όταν το επόμενο βήμα είναι μικρό, συγκεκριμένο και μετρήσιμο."],
    "joke": ["Γιατί το τοπικό AI απέφυγε το cloud; Είχε πολλά προβλήματα σύνδεσης.", "Ο προγραμματιστής μπήκε στο cache για να βρει προσωρινή ηρεμία."],
    "bored": ["Διάλεξε ένα: μάθε μου πέντε χρήσιμα στοιχεία, εισήγαγε ένα έγγραφο, γράψε ένα μικρό εργαλείο Python ή οργάνωσε δέκα αρχεία.", "Δοκίμασε ένα εικοσάλεπτο έργο με ορατό αποτέλεσμα, όπως ένα terminal quiz."],
    "coding": ["Περιέγραψε την είσοδο, την επιθυμητή έξοδο, τους περιορισμούς και το ακριβές σφάλμα.", "Για αξιόπιστη διόρθωση κώδικα χρειάζομαι το σχετικό τμήμα και ολόκληρο το traceback."],
    "debugging": ["Διάβασε το traceback από την τελευταία γραμμή προς τα πάνω και εντόπισε το πρώτο σημείο που ανήκει στον δικό σου κώδικα.", "Έλεγξε ονόματα μεταβλητών, τύπους, διαδρομές, δικαιώματα και τις πραγματικές τιμές πριν από τη γραμμή του σφάλματος."],
    "git": ["Οι βασικές εντολές Git είναι git status, git add, git commit, git pull και git push.", "Πριν από merge ή pull, έλεγξε το git status και δημιούργησε ασφαλές commit ή backup."],
    "networking": ["Η δικτύωση περιλαμβάνει διευθύνσεις IP, θύρες, DNS, δρομολόγηση και πρωτόκολλα.", "Για διάγνωση ξεκίνα από σύνδεση, διεύθυνση, DNS, προσβασιμότητα θύρας και logs."],
    "cybersecurity": ["Χρησιμοποίησε μοναδικούς κωδικούς, password manager, πολυπαραγοντικό έλεγχο, ενημερώσεις και δοκιμασμένα αντίγραφα ασφαλείας.", "Αντιμετώπισε απρόσμενους συνδέσμους, συνημμένα, αιτήματα σύνδεσης και τεχνητή πίεση ως προειδοποιητικά σημάδια."],
    "passwords": ["Χρησιμοποίησε διαφορετικό τυχαίο κωδικό για κάθε σημαντικό λογαριασμό και αποθήκευσέ τον σε αξιόπιστο password manager.", "Το μήκος και η μοναδικότητα είναι σημαντικότερα από προβλέψιμες αντικαταστάσεις χαρακτήρων. Ενεργοποίησε 2FA."],
    "phishing": ["Το phishing μιμείται αξιόπιστη οντότητα για να κλέψει στοιχεία, χρήματα ή δεδομένα. Άνοιξε μόνος σου την επίσημη εφαρμογή ή ιστοσελίδα.", "Η πίεση χρόνου, τα απρόσμενα συνημμένα, οι λάθος domains και τα αιτήματα για μυστικά είναι συνηθισμένες ενδείξεις."],
    "malware": ["Το malware είναι λογισμικό που βλάπτει, κατασκοπεύει ή αποκτά μη εξουσιοδοτημένη πρόσβαση. Αφαίρεσε ύποπτες εφαρμογές, ενημέρωσε τη συσκευή και έλεγξε δικαιώματα.", "Εγκαθιστάς εφαρμογές μόνο από αξιόπιστες πηγές και δεν δίνεις άσχετα δικαιώματα."],
    "backup": ["Κράτησε πολλαπλά αντίγραφα σημαντικών δεδομένων, με τουλάχιστον ένα χωριστά από το κινητό, και δοκίμασε την επαναφορά.", "Η εντολή /backup αρχειοθετεί το μοντέλο, το dataset, τις μνήμες και την τοπική γνώση."],
    "updates": ["Στο Termux το pkg update ανανεώνει τις λίστες και το pkg upgrade εγκαθιστά διαθέσιμες ενημερώσεις.", "Πάρε backup σημαντικών scripts πριν από μεγάλη αναβάθμιση Python ή πακέτων."],
    "ai": ["Η τεχνητή νοημοσύνη είναι πεδίο συστημάτων που εκτελούν εργασίες αντίληψης, πρόβλεψης, γλώσσας, σχεδιασμού ή λήψης αποφάσεων.", "Αυτός ο βοηθός χρησιμοποιεί στενές μεθόδους AI: ταξινόμηση, ανάκτηση πληροφοριών και στατιστική παραγωγή κειμένου."],
    "machine_learning": ["Η μηχανική μάθηση προσαρμόζει παραμέτρους από παραδείγματα. Στην επιβλεπόμενη ταξινόμηση κάθε είσοδος έχει γνωστή ετικέτα.", "Η ποιότητα δεδομένων, η αντιπροσωπευτικότητα, η επικύρωση και η ανάλυση σφαλμάτων είναι εξίσου σημαντικές με το μέγεθος μοντέλου."],
    "neural_network": ["Ένα νευρωνικό δίκτυο εφαρμόζει μαθημένους σταθμισμένους μετασχηματισμούς. Το backpropagation υπολογίζει τη συμβολή κάθε βάρους στο σφάλμα.", "Το PocketAI χρησιμοποιεί sparse hashed χαρακτηριστικά, δύο κρυφά επίπεδα tanh και έξοδο softmax."],
    "limitations": ["Δεν είμαι μεγάλο γλωσσικό μοντέλο. Η ενσωματωμένη γνώση μου είναι περιορισμένη και αποδίδω καλύτερα με /teach και /ingest.", "Μπορώ να ταξινομήσω λάθος άγνωστο κείμενο ή να βρω επιφανειακά παρόμοιο απόσπασμα. Έλεγχε σημαντικές απαντήσεις."],
    "memory": ["Χρησιμοποίησε /remember key = value για αποθήκευση, /memories για προβολή και /forget key για διαγραφή.", "Οι μνήμες αποθηκεύονται τοπικά σε SQLite και παραμένουν μετά την επανεκκίνηση."],
    "documents": ["Χρησιμοποίησε /ingest PATH για να δημιουργήσεις ευρετήριο από αρχεία ή φάκελο και μετά κάνε ερωτήσεις με σχετικές λέξεις.", "Η τοπική αναζήτηση εγγράφων μπορεί να κρατήσει πολύ περισσότερη γνώση από τον νευρωνικό ταξινομητή."],
    "teach": ["Χρησιμοποίησε /teach ερώτηση | απάντηση για άμεση μόνιμη γνώση.", "Τα ζεύγη ερώτησης και απάντησης ευρετηριάζονται αμέσως και δεν χρειάζονται νευρωνική επανεκπαίδευση."],
    "creator": ["Αυτό το τοπικό build ανήκει στο άτομο που το εκτελεί. Μπορείς να ορίσεις δημιουργό με /remember creator = όνομα.", "Είμαι ένα αυτοτελές πρόγραμμα Python που μπορείς να προσαρμόσεις από τα τοπικά αρχεία."],
    "dedsec": ["Το DedSec Project είναι το ευρύτερο έργο εργαλείων Termux και κυβερνοασφάλειας του χρήστη. Εισήγαγε το README του με /ingest για συγκεκριμένες απαντήσεις.", "Μπορείς να με μετατρέψεις σε βοηθό του DedSec Project διδάσκοντάς μου στοιχεία με /teach."],
    "unknown": ["Ίσως χρειάζομαι περισσότερη τοπική γνώση. Χρησιμοποίησε /teach ή /ingest.", "Δεν αντιστοίχισα το αίτημα με αρκετή βεβαιότητα. Κάνε πιο συγκεκριμένη ερώτηση."],
}

FALLBACK_RESPONSES = {
    "en": [
        "I do not have a reliable local answer for that yet. Use /teach or /ingest to add knowledge.",
        "I am uncertain. Try a more specific question or teach me a direct answer with /teach.",
        "That is outside my current model and indexed memory."
    ],
    "el": [
        "Δεν έχω ακόμη αξιόπιστη τοπική απάντηση. Πρόσθεσε γνώση με /teach ή /ingest.",
        "Δεν είμαι βέβαιο. Κάνε πιο συγκεκριμένη ερώτηση ή δίδαξέ μου άμεση απάντηση με /teach.",
        "Αυτό βρίσκεται έξω από το τρέχον μοντέλο και την ευρετηριασμένη μνήμη μου."
    ]
}

GREEK_WEEKDAYS = ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"]
GREEK_MONTHS = ["Ιανουαρίου", "Φεβρουαρίου", "Μαρτίου", "Απριλίου", "Μαΐου", "Ιουνίου", "Ιουλίου", "Αυγούστου", "Σεπτεμβρίου", "Οκτωβρίου", "Νοεμβρίου", "Δεκεμβρίου"]


INTENT_HINTS = {
    "training": {"retrain": 0.96, "train the model": 0.96, "training model": 0.90, "neural training": 0.92, "train you": 0.98, "how do i train": 0.99, "how can i train": 0.98},
    "teach": {"teach you": 0.90, "add an answer": 0.92, "add new information": 0.97, "save question": 0.88, "custom knowledge": 0.86},
    "privacy": {"upload": 0.78, "send my data": 0.92, "track me": 0.90, "data private": 0.92, "privacy": 0.82},
    "offline": {"offline": 0.94, "no connection": 0.88, "without internet": 0.94, "without wifi": 0.96, "no wifi": 0.96, "need internet": 0.90},
    "passwords": {"password": 0.88, "passwords": 0.90, "passphrase": 0.82, "login secret": 0.76},
    "phishing": {"phishing": 0.96, "suspicious email": 0.92, "strange login email": 0.96, "weird email": 0.92, "fake login": 0.92, "scam message": 0.86},
    "malware": {"malware": 0.96, "virus": 0.90, "trojan": 0.94, "ransomware": 0.96, "malicious app": 0.90},
    "study": {"study": 0.88, "school": 0.76, "exam": 0.88, "homework": 0.82, "learn for": 0.70},
    "motivation": {"motivate": 0.94, "motivation": 0.94, "encouragement": 0.86, "cannot start": 0.84, "need to begin": 0.78},
    "joke": {"joke": 0.96, "make me laugh": 0.96, "funny": 0.76},
    "ai": {"artificial intelligence": 0.96, "what is ai": 0.96, " ai model": 0.78},
    "machine_learning": {"machine learning": 0.98, "supervised learning": 0.94, "training data": 0.82},
    "neural_network": {"neural network": 0.98, "neural net": 0.96, "neural weights": 0.98, "weights learned": 0.96, "backprop": 0.96, "hidden layer": 0.92, "softmax": 0.90},
    "documents": {"document": 0.84, "ingest": 0.96, "index notes": 0.92, "local notes": 0.93, "my notes": 0.90, "text file": 0.78},
    "memory": {"remember": 0.78, "memory": 0.82, "forget": 0.70},
    "debugging": {"traceback": 0.96, "debug": 0.90, "syntax error": 0.94, "python exception": 0.96, "python error": 0.94, "nameerror": 0.96, "typeerror": 0.96},
    "updates": {"update packages": 0.94, "upgrade packages": 0.94, "pkg update": 0.98, "software update": 0.82},
    "battery": {"overheating": 0.96, "battery": 0.90, "phone gets hot": 0.94, "very hot": 0.92, "drains battery": 0.90},
    "date": {"today's date": 0.98, "todays date": 0.98, "current date": 0.96, "what day": 0.84, "date is it": 0.92},
    "time": {"what time": 0.96, "current time": 0.96, "clock time": 0.90, "tell me the time": 0.96},
    "weather": {"weather": 0.96, "will it rain": 0.96, "temperature outside": 0.94, "forecast": 0.88},
    "news": {"latest news": 0.98, "headlines": 0.94, "breaking news": 0.98, "current events": 0.92, "news today": 0.94},
    "networking": {"network port": 0.96, "ip address": 0.96, "dns": 0.90, "router": 0.88, "localhost": 0.90, "networking": 0.94},
    "cybersecurity": {"cybersecurity": 0.98, "secure my phone": 0.92, "stay safe online": 0.94, "protect my account": 0.90},
    "termux": {"termux": 0.98, "need root": 0.90, "android terminal": 0.92},
    "calculator": {"calculate": 0.82, "calculator": 0.96, "arithmetic": 0.84},
    "coding": {"source code": 0.86, "programming help": 0.90, "help me code": 0.94},
    "git": {" git ": 0.90, "github": 0.86, "clone repository": 0.94, "git commit": 0.96},
    "backup": {"backup": 0.94, "restore files": 0.90, "copy important files": 0.84, "preserve my files": 0.94, "safe copies": 0.92},
    "limitations": {"unable to do": 0.96, "what can you not": 0.96, "what are you unable": 0.96, "limitations": 0.94, "weaknesses": 0.92}
}


# High-confidence Greek routing hints complement the neural and fuzzy routes.
_GREEK_HINTS = {
    "training": {"εκπαιδευση μοντελου": 0.96, "επανεκπαιδευση": 0.96, "πως εκπαιδευεσαι": 0.90},
    "teach": {"να σου μαθω": 0.94, "προσθεσε απαντηση": 0.92, "νεα γνωση": 0.86, "προσθεσω νεα γνωση": 0.97, "προσθεσω πληροφοριες": 0.96},
    "privacy": {"προσωπικα δεδομενα": 0.94, "στελνεις τα δεδομενα": 0.96, "ιδιωτικοτητα": 0.90},
    "offline": {"χωρισ ιντερνετ": 0.96, "δουλευεις offline": 0.96, "χωρισ συνδεση": 0.92, "δουλεψεισ χωρισ wifi": 0.97, "δουλεψει χωρισ wifi": 0.97},
    "passwords": {"κωδικος προσβασης": 0.96, "ισχυρος κωδικος": 0.94, "password manager": 0.90},
    "phishing": {"ηλεκτρονικο ψαρεμα": 0.98, "υποπτο μηνυμα": 0.94, "περιεργο email συνδεσης": 0.97, "ψευτικη συνδεση": 0.92},
    "malware": {"κακοβουλο λογισμικο": 0.98, "ιος στο κινητο": 0.94, "υποπτη εφαρμογη": 0.90},
    "study": {"πως να διαβασω": 0.94, "προετοιμασια εξετασεων": 0.94, "βοηθεια στο διαβασμα": 0.92},
    "motivation": {"δωσε κινητρο": 0.96, "δεν μπορω να ξεκινησω": 0.94, "βαριεμαι να αρχισω": 0.90},
    "joke": {"πες αστειο": 0.98, "κανε με να γελασω": 0.98},
    "ai": {"τεχνητη νοημοσυνη": 0.98, "μοντελο ai": 0.94},
    "machine_learning": {"μηχανικη μαθηση": 0.98, "δεδομενα εκπαιδευσης": 0.92},
    "neural_network": {"νευρωνικο δικτυο": 0.98, "κρυφο επιπεδο": 0.92},
    "documents": {"διαβασε αρχειο": 0.96, "αναζητηση εγγραφων": 0.94, "εισαγωγη σημειωσεων": 0.90, "σημειωσεις μου": 0.94, "ψαξεισ στις σημειωσεις": 0.96},
    "memory": {"θυμησου": 0.92, "τι θυμασαι": 0.94, "ξεχασε": 0.84},
    "debugging": {"σφαλμα python": 0.96, "σφαλμα σε προγραμμα": 0.96, "αποσφαλματωση": 0.94, "traceback": 0.96},
    "updates": {"ενημερωση termux": 0.96, "αναβαθμιση πακετων": 0.96},
    "battery": {"ζεσταινεται το κινητο": 0.98, "μπαταρια": 0.92, "καταναλωση μπαταριας": 0.94, "κινητο καιει": 0.97, "κατα την εκπαιδευση": 0.88},
    "date": {"τι ημερομηνια": 0.98, "τι μερα ειναι": 0.94},
    "time": {"τι ωρα ειναι": 0.98, "πες την ωρα": 0.96},
    "weather": {"τι καιρο κανει": 0.98, "θα βρεξει": 0.96, "προγνωση καιρου": 0.94},
    "news": {"τελευταιες ειδησεις": 0.98, "τι εγινε σημερα": 0.96, "νεα σημερα": 0.94},
    "networking": {"διευθυνση ip": 0.98, "θυρα δικτυου": 0.96, "δικτυωση": 0.94},
    "cybersecurity": {"κυβερνοασφαλεια": 0.98, "ασφαλεια στο ιντερνετ": 0.96, "προστασια λογαριασμου": 0.94, "προστατευω τον λογαριασμο": 0.97},
    "termux": {"τι ειναι το termux": 0.98, "χρειαζεται root": 0.94, "τερματικο android": 0.92},
    "calculator": {"υπολογισε": 0.94, "αριθμομηχανη": 0.98, "κανε υπολογισμο": 0.96},
    "coding": {"βοηθεια στον κωδικα": 0.96, "γραψε προγραμμα": 0.92, "προγραμματισμος": 0.90},
    "git": {"εντολες git": 0.96, "github": 0.88, "κλωνοποιηση repository": 0.94},
    "backup": {"αντιγραφο ασφαλειας": 0.98, "επαναφορα αρχειων": 0.94, "αντιγραφα των αρχειων": 0.96},
    "limitations": {"τι δεν μπορεις": 0.98, "περιορισμοι": 0.94, "τι δεν μπορεισ": 0.98}
}
for _tag, _hints in _GREEK_HINTS.items():
    INTENT_HINTS.setdefault(_tag, {}).update(_hints)


# ---------------------------------------------------------------------------
# Built-in English and Greek training data
# ---------------------------------------------------------------------------


def _intent(tag: str, patterns: Sequence[str], responses: Sequence[str]) -> dict:
    return {"tag": tag, "patterns": list(patterns), "responses": list(responses)}


DEFAULT_INTENTS = [
    _intent("greeting", [
        "hello", "hi", "hey", "hello there", "good morning", "good afternoon",
        "good evening", "are you there", "hi assistant", "hey pocket ai",
        "γεια", "γεια σου", "καλημέρα", "καλησπέρα", "είσαι εκεί"
    ], [
        "Hello{name_suffix}. I am ready.",
        "Hi{name_suffix}. What should we work on?",
        "I am here and running locally on this phone.",
        "Γεια σου{name_suffix}. Είμαι έτοιμο."
    ]),
    _intent("goodbye", [
        "bye", "goodbye", "see you", "see you later", "talk later", "I have to go",
        "close chat", "exit assistant", "good night", "αντίο", "τα λέμε", "καληνύχτα"
    ], [
        "Goodbye{name_suffix}.", "See you later.", "The local session is closing.",
        "Αντίο{name_suffix}."
    ]),
    _intent("identity", [
        "who are you", "what are you", "what is your name", "tell me your name",
        "are you artificial intelligence", "are you an ai", "describe yourself",
        "who made you", "what model are you", "ποιος είσαι", "τι είσαι", "πως σε λένε"
    ], [
        "I am PocketAI MAX, a hybrid offline assistant built from scratch in standard Python.",
        "I combine a small neural network, indexed retrieval memory, and local utilities.",
        "My name is PocketAI MAX. I run without root, cloud APIs, or heavy AI frameworks."
    ]),
    _intent("capabilities", [
        "what can you do", "how can you help", "show your abilities", "show features",
        "what do you know", "can you learn", "can I teach you", "what are your functions",
        "list your capabilities", "τι μπορείς να κάνεις", "πως μπορείς να βοηθήσεις"
    ], [
        "I can classify requests, retrieve taught answers, index text documents, remember facts, calculate expressions, and run offline utilities.",
        "Use /help for commands. My knowledge can grow through /teach, /remember, and /ingest.",
        "I am best at custom offline assistance, FAQs, notes, document search, and lightweight automation guidance."
    ]),
    _intent("help", [
        "help", "show help", "show commands", "commands", "usage", "how do I use you",
        "what commands exist", "command list", "βοήθεια", "δείξε εντολές", "πως σε χρησιμοποιώ"
    ], [
        "Type /help to see every command, including teaching, document ingestion, memories, training, statistics, backup, and generation."
    ]),
    _intent("thanks", [
        "thanks", "thank you", "many thanks", "that helped", "great job", "nice work",
        "perfect", "very helpful", "excellent", "ευχαριστώ", "σε ευχαριστώ", "τέλεια"
    ], [
        "You are welcome{name_suffix}.", "Glad it helped.", "Understood."
    ]),
    _intent("apology", [
        "sorry", "my mistake", "I apologize", "forgive me", "oops", "συγγνώμη", "λάθος μου"
    ], [
        "No problem.", "That is fine. We can continue.", "Δεν υπάρχει πρόβλημα."
    ]),
    _intent("status", [
        "how are you", "are you working", "model status", "are you running",
        "is everything okay", "system status", "how do you feel", "πως είσαι", "δουλεύεις"
    ], [
        "I am running normally. Use /stats for technical details.",
        "The assistant is loaded and ready.",
        "Everything appears operational."
    ]),
    _intent("offline", [
        "do you need internet", "are you offline", "does this work offline",
        "internet required", "can you work without wifi", "do you use cloud",
        "χρειάζεσαι ίντερνετ", "δουλεύεις offline", "λειτουργείς χωρίς σύνδεση"
    ], [
        "I run offline after Python is installed. Neural inference, memory, and document search stay on the device.",
        "No internet is required for my normal operation.",
        "I do not call a cloud AI service."
    ]),
    _intent("privacy", [
        "is my data private", "do you send my data", "where is data stored",
        "are chats uploaded", "privacy", "do you track me", "is this secure",
        "είναι ιδιωτικά τα δεδομένα", "στέλνεις τα δεδομένα μου"
    ], [
        "Your model, memories, documents, and chat history are stored locally under {data_dir}.",
        "This script does not upload chats. Protect the phone and its storage because local files can still be read by anyone with device access.",
        "Use /where to see the exact local storage paths."
    ]),
    _intent("training", [
        "how are you trained", "how do I train you", "train the model", "retrain",
        "how does learning work", "where is the dataset", "neural training",
        "πως εκπαιδεύεσαι", "πως κάνω training", "εκπαίδευση μοντέλου"
    ], [
        "The neural classifier learns from dataset.json with backpropagation. Run /train after changing intent examples.",
        "Use /teach for instant retrieval knowledge. Neural intent changes belong in dataset.json and require /train.",
        "Training uses hashed text features and two hidden layers, then stores a compressed local model."
    ]),
    _intent("termux", [
        "what is termux", "does this run in termux", "termux support", "android terminal",
        "can I use this on android", "does it need root", "old android phone",
        "low end phone", "τι είναι το termux", "τρέχει σε android", "χρειάζεται root"
    ], [
        "This assistant is designed for Python in Termux and does not require root.",
        "It avoids TensorFlow and PyTorch so it can run on older Android hardware.",
        "Install Python in Termux, copy this file, and run it normally."
    ]),
    _intent("android", [
        "tell me about android", "android phone", "android operating system",
        "phone performance", "old samsung", "galaxy j6", "android storage",
        "πες μου για android", "παλιό κινητό"
    ], [
        "Android can run local Python through Termux. Performance depends on RAM, thermal limits, and background apps.",
        "For older phones, use the balanced or max profile and keep large document collections reasonable.",
        "The assistant is CPU-only and stores its files in the selected data directory."
    ]),
    _intent("python", [
        "what is python", "learn python", "python programming", "python error",
        "run python script", "install python", "python language", "τι είναι python",
        "πως τρέχω python"
    ], [
        "Python is a general-purpose programming language. In Termux, install it with pkg install python.",
        "For a Python error, provide the complete traceback and the relevant code around the failing line.",
        "This entire assistant is implemented with Python's standard library."
    ]),
    _intent("linux", [
        "what is linux", "linux command", "terminal command", "shell help",
        "bash command", "filesystem linux", "permissions chmod", "τι είναι linux",
        "εντολές linux"
    ], [
        "Linux-like environments organize files under directories and use commands such as ls, cd, cp, mv, and chmod.",
        "Use pwd to show the current directory and ls -la to inspect files and permissions.",
        "Be careful with destructive commands such as rm -rf; verify the path first."
    ]),
    _intent("files", [
        "where are my files", "how do I copy a file", "move file", "rename file",
        "delete file", "list files", "file path", "find a file", "που είναι τα αρχεία",
        "αντιγραφή αρχείου"
    ], [
        "In Termux, ls lists files, cp copies, mv moves or renames, and rm deletes. Quote paths containing spaces.",
        "Use /where for PocketAI files. Shared Downloads are usually available through ~/storage/downloads after termux-setup-storage.",
        "Always inspect a target path before deleting or overwriting files."
    ]),
    _intent("storage", [
        "storage space", "disk space", "phone is full", "check free space",
        "termux storage permission", "access downloads", "χώρος αποθήκευσης",
        "γεμάτη μνήμη"
    ], [
        "Run df -h to inspect storage. In Termux, termux-setup-storage creates shortcuts after Android grants permission.",
        "Use /system for a quick local storage and memory summary.",
        "Large indexed documents and backups consume more space than the neural model itself."
    ]),
    _intent("battery", [
        "battery usage", "save battery", "phone gets hot", "overheating",
        "training drains battery", "battery optimization", "μπαταρία", "ζεσταίνεται το κινητό"
    ], [
        "Neural training uses sustained CPU. Keep the phone ventilated, avoid charging under heavy heat, and use the balanced profile if needed.",
        "Inference is light; first-run training and large ingestion jobs use more battery.",
        "Close unnecessary background apps before a large training run."
    ]),
    _intent("time", [
        "what time is it", "tell me the time", "current time", "local time",
        "ώρα", "τι ώρα είναι", "πες μου την ώρα"
    ], [
        "The local time is {time}.", "It is {time} on this device."
    ]),
    _intent("date", [
        "what date is it", "today's date", "what day is today", "current date",
        "ημερομηνία", "τι μέρα είναι", "τι ημερομηνία έχουμε"
    ], [
        "The local date is {date}.", "Today is {date}."
    ]),
    _intent("weather", [
        "what is the weather", "weather forecast", "will it rain", "temperature outside",
        "καιρός", "τι καιρό κάνει", "θα βρέξει"
    ], [
        "I cannot know live weather while fully offline. You can teach me static climate notes, but current forecasts require an external data source.",
        "Live weather changes constantly and is not available to this offline model."
    ]),
    _intent("news", [
        "latest news", "what happened today", "current events", "breaking news",
        "νέα", "ειδήσεις", "τι έγινε σήμερα"
    ], [
        "I cannot verify current news without an internet source. You can ingest downloaded articles and search them locally.",
        "My built-in knowledge is static; current events require fresh external information."
    ]),
    _intent("calculator", [
        "can you calculate", "do math", "calculator", "solve arithmetic",
        "calculate expression", "κάνε υπολογισμό", "αριθμομηχανή"
    ], [
        "Start a message with = or calc, for example: = (12 + 8) * 3.",
        "I include a safe offline calculator supporting arithmetic and selected mathematical functions."
    ]),
    _intent("math", [
        "what is mathematics", "help with algebra", "geometry help", "math problem",
        "equation", "percentage", "average", "μαθηματικά", "άλγεβρα", "εξίσωση"
    ], [
        "Give me a concrete arithmetic expression with = for calculation. For symbolic problems, explain the variables and the required result.",
        "Mathematics becomes easier when the known values, unknowns, and constraints are written explicitly.",
        "For percentages: percentage = part divided by total, multiplied by 100."
    ]),
    _intent("science", [
        "tell me about science", "physics", "chemistry", "biology", "scientific method",
        "experiment", "επιστήμη", "φυσική", "χημεία", "βιολογία"
    ], [
        "The scientific method uses observations, testable hypotheses, controlled experiments, evidence, and reproducible analysis.",
        "Ask a specific science question or ingest reference notes for local retrieval.",
        "Good scientific conclusions distinguish measured evidence from assumptions."
    ]),
    _intent("history", [
        "tell me history", "historical event", "ancient history", "world history",
        "ιστορία", "ιστορικό γεγονός", "αρχαία ιστορία"
    ], [
        "Ask about a specific period, place, or event. For detailed accuracy, ingest a trusted reference document and query it locally.",
        "Historical analysis should separate primary evidence, later interpretation, and uncertainty."
    ]),
    _intent("geography", [
        "geography", "countries", "capital city", "continents", "maps",
        "γεωγραφία", "χώρες", "πρωτεύουσα"
    ], [
        "Ask a specific geography question. Static facts can be taught with /teach or loaded from a text document.",
        "Geography covers physical landscapes, human settlement, borders, climate, and spatial relationships."
    ]),
    _intent("study", [
        "help me study", "study tips", "how to learn", "memorize better", "exam preparation",
        "focus on studying", "διάβασμα", "πως να μάθω", "εξετάσεις"
    ], [
        "Use active recall, spaced repetition, short focused sessions, and practice questions instead of rereading alone.",
        "Break the subject into small objectives, test yourself, then revisit weak areas.",
        "You can ingest your notes and ask me to retrieve matching passages offline."
    ]),
    _intent("motivation", [
        "motivate me", "I feel lazy", "I cannot start", "need motivation",
        "encourage me", "give me confidence", "κίνητρο", "δεν μπορώ να ξεκινήσω"
    ], [
        "Reduce the task to one action that takes less than five minutes, then begin before evaluating your motivation.",
        "Progress is easier to sustain when the next step is specific and small.",
        "Start with one measurable action. Momentum can follow action rather than precede it."
    ]),
    _intent("joke", [
        "tell me a joke", "make me laugh", "say something funny", "joke",
        "πες αστείο", "κάνε με να γελάσω"
    ], [
        "Why did the local AI refuse the cloud? It had too many attachment issues.",
        "A programmer's favorite place is the cache. It is where everything temporarily makes sense.",
        "I tried to tell a recursion joke, but first I had to tell a recursion joke."
    ]),
    _intent("bored", [
        "I am bored", "nothing to do", "give me an activity", "boredom",
        "βαριέμαι", "δεν έχω τι να κάνω"
    ], [
        "Choose one: teach me five useful facts, index a document, write a tiny Python tool, or organize ten files.",
        "Try a twenty-minute project with a visible result, such as a terminal quiz or personal knowledge file.",
        "Use /ingest on notes you care about, then test how well I retrieve them."
    ]),
    _intent("coding", [
        "help me code", "programming help", "write software", "coding project",
        "how to program", "source code", "βοήθεια με κώδικα", "προγραμματισμός"
    ], [
        "Define the input, expected output, constraints, and failure cases before implementing the program.",
        "For coding help, provide the language, complete error, relevant code, and expected behavior.",
        "Build in small testable functions and validate each stage before adding more features."
    ]),
    _intent("debugging", [
        "fix my error", "debug code", "program crashes", "traceback", "syntax error",
        "name error", "type error", "διόρθωσε το λάθος", "σφάλμα κώδικα"
    ], [
        "Read the traceback from the final line upward, identify the first line in your own code, and inspect the values used there.",
        "Provide the complete traceback and the surrounding function. Error text without code often hides the real cause.",
        "Reproduce the failure with the smallest input possible before changing several parts at once."
    ]),
    _intent("git", [
        "what is git", "git command", "github", "clone repository", "commit changes",
        "push code", "pull updates", "τι είναι git", "εντολές git"
    ], [
        "Git tracks file history. Common commands include git status, git add, git commit, git pull, and git push.",
        "Before destructive Git operations, inspect git status and create a backup or branch.",
        "Use git clone URL to copy a repository, then cd into its folder."
    ]),
    _intent("networking", [
        "what is an ip address", "network help", "wifi problem", "dns", "router",
        "localhost", "port", "δικτύωση", "διεύθυνση ip", "θύρα δικτύου"
    ], [
        "An IP address identifies a network interface, while a port identifies a service endpoint on that host.",
        "127.0.0.1 is the local loopback address and is reachable only from the same device unless a service binds elsewhere.",
        "Diagnose networking layer by layer: interface, address, route, DNS, connection, then application."
    ]),
    _intent("cybersecurity", [
        "cybersecurity", "stay safe online", "protect my account", "security tips",
        "online safety", "secure phone", "κυβερνοασφάλεια", "ασφάλεια στο ίντερνετ"
    ], [
        "Use unique passwords, a password manager, multi-factor authentication, current software, and verified backups.",
        "Treat unexpected links, attachments, login prompts, and urgency as warning signs.",
        "Security is risk reduction: minimize exposed services, permissions, reused credentials, and unverified software."
    ]),
    _intent("passwords", [
        "strong password", "password security", "forgot password", "password manager",
        "reuse password", "κωδικός πρόσβασης", "ισχυρός κωδικός"
    ], [
        "Use a unique randomly generated password for every important account and store it in a reputable password manager.",
        "Length and uniqueness matter more than predictable substitutions. Enable multi-factor authentication where possible.",
        "Never send passwords or recovery codes through ordinary chat."
    ]),
    _intent("phishing", [
        "what is phishing", "suspicious email", "fake login", "scam message",
        "malicious link", "phishing attack", "ηλεκτρονικό ψάρεμα", "ύποπτο μήνυμα"
    ], [
        "Phishing impersonates a trusted party to steal credentials, money, or data. Verify the sender and navigate through the official app or site rather than the supplied link.",
        "Urgency, unexpected attachments, mismatched domains, and requests for secrets are common phishing indicators.",
        "Do not enter credentials after following an unverified message link."
    ]),
    _intent("malware", [
        "what is malware", "phone virus", "trojan", "ransomware", "malicious app",
        "remove malware", "κακόβουλο λογισμικό", "ιός στο κινητό"
    ], [
        "Malware is software designed to harm, spy, disrupt, or gain unauthorized access. Remove suspicious apps, update the device, review permissions, and preserve important evidence before resetting.",
        "Install applications only from trusted sources and avoid granting permissions unrelated to their function.",
        "A factory reset can remove many infections, but backup and account recovery planning should come first."
    ]),
    _intent("backup", [
        "make a backup", "backup data", "restore files", "copy important files",
        "backup strategy", "αντίγραφο ασφαλείας", "backup αρχείων"
    ], [
        "Keep multiple copies of important data, with at least one copy separated from the phone. Test that restoration actually works.",
        "Use /backup to archive PocketAI's local model, dataset, memories, and indexed knowledge.",
        "A backup is only reliable after a successful restore test."
    ]),
    _intent("updates", [
        "update termux", "update packages", "software update", "upgrade python",
        "package update", "ενημέρωση termux", "αναβάθμιση πακέτων"
    ], [
        "In Termux, pkg update refreshes package lists and pkg upgrade installs available updates. Review errors before forcing changes.",
        "Back up important scripts before a major runtime or package upgrade.",
        "After updating Python, rerun PocketAI and rebuild the local model if its saved format becomes incompatible."
    ]),
    _intent("ai", [
        "what is ai", "artificial intelligence", "how does ai work", "ai model",
        "machine intelligence", "τεχνητή νοημοσύνη", "μοντέλο ai"
    ], [
        "Artificial intelligence is a broad field of systems performing tasks associated with perception, prediction, language, planning, or decision-making.",
        "This assistant uses narrow AI methods: supervised classification, information retrieval, and statistical text generation.",
        "AI output should be evaluated against evidence because confidence and fluency do not guarantee correctness."
    ]),
    _intent("machine_learning", [
        "what is machine learning", "supervised learning", "training data",
        "classification model", "features and labels", "μηχανική μάθηση"
    ], [
        "Machine learning fits parameters from examples. In supervised classification, inputs have known labels used to calculate training error.",
        "Data quality, representative examples, validation, and error analysis matter as much as model size.",
        "PocketAI's classifier maps hashed text features to intent labels."
    ]),
    _intent("neural_network", [
        "what is a neural network", "hidden layer", "backpropagation", "softmax",
        "activation function", "deep learning", "νευρωνικό δίκτυο", "backpropagation"
    ], [
        "A neural network applies learned weighted transformations. Backpropagation calculates how each weight contributed to prediction error.",
        "PocketAI uses sparse hashed input features, two tanh hidden layers, and a softmax output over intents.",
        "Larger networks can represent more patterns but require more computation, data, and careful validation."
    ]),
    _intent("limitations", [
        "what are your limitations", "are you like chatgpt", "can you understand everything",
        "do you hallucinate", "how smart are you", "weaknesses", "περιορισμοί"
    ], [
        "I am not a large language model. I have limited built-in knowledge and work best with taught answers and indexed documents.",
        "I can misclassify unfamiliar text or retrieve a superficially similar passage. Verify important answers.",
        "My strength is private, lightweight, customizable offline assistance rather than broad open-ended reasoning."
    ]),
    _intent("memory", [
        "can you remember", "what do you remember", "long term memory", "save a fact",
        "forget something", "personal memory", "θυμάσαι", "μνήμη"
    ], [
        "Use /remember key = value to store a local memory, /memories to list keys, and /forget key to remove one.",
        "My persistent memories are stored locally in SQLite and remain available after restart.",
        "Do not store secrets that should not exist in plain local application data."
    ]),
    _intent("documents", [
        "read my document", "search documents", "ingest file", "index notes",
        "learn from text file", "document knowledge", "διάβασε αρχείο", "αναζήτηση εγγράφων"
    ], [
        "Use /ingest PATH to index text files or a folder. Then ask questions using words that occur in the material.",
        "Document retrieval is local and can hold much more knowledge than the neural classifier itself.",
        "Plain text, Markdown, code, CSV, JSON, HTML, and several configuration formats are supported."
    ]),
    _intent("teach", [
        "teach you something", "add an answer", "learn this question", "custom knowledge",
        "save question and answer", "να σου μάθω", "πρόσθεσε απάντηση"
    ], [
        "Use /teach question | answer for immediate persistent knowledge, or run /teach interactively.",
        "Taught question-and-answer pairs are indexed immediately and do not require neural retraining.",
        "For a new broad intent, edit dataset.json and run /train."
    ]),
    _intent("creator", [
        "who created pocket ai", "who is the creator", "who wrote this",
        "who built you", "author", "ποιος σε έφτιαξε"
    ], [
        "This local build belongs to the person running it. You can set creator information with /remember creator = your name.",
        "I am a self-contained Python program that can be customized by editing its local files."
    ]),
    _intent("dedsec", [
        "dedsec project", "what is dedsec", "ded sec", "ded-sec.space",
        "dedsec tools", "project creator"
    ], [
        "DedSec Project is the user's broader Termux and cybersecurity-tool project. Store current project facts with /teach or index its documentation with /ingest.",
        "You can make me a project assistant by ingesting the DedSec README and teaching project-specific questions."
    ]),
    _intent("unknown", [
        "something unrelated", "random unknown request", "unrecognized words",
        "question outside training", "I need a different topic"
    ], [
        "I may need more local knowledge for that. Use /teach or /ingest to extend me.",
        "That does not closely match my built-in intents. I can learn a direct answer with /teach."
    ])
]

DEFAULT_DATASET = {
    "dataset_version": DATASET_VERSION,
    "assistant_name": APP_NAME,
    "language": "English and Greek only",
    "fallback_responses": [
        "I do not have a reliable local answer for that yet. Use /teach or /ingest to add knowledge.",
        "That request is outside my current model and indexed memory.",
        "I am uncertain. Teach me a direct answer with /teach question | answer.",
        "I could not match that confidently. Try a more specific question or index relevant notes."
    ],
    "intents": DEFAULT_INTENTS
}


# ---------------------------------------------------------------------------
# General helpers
# ---------------------------------------------------------------------------


def default_data_dir() -> Path:
    override = os.environ.get("POCKETAI_HOME")
    if override:
        return Path(override).expanduser()
    return Path(__file__).resolve().parent / "Other Files" / "Saved Data"


def human_size(size: int) -> str:
    units = ("B", "KB", "MB", "GB", "TB", "PB", "EB")
    value = float(max(0, size))
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{size} B"


def now_iso() -> str:
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def atomic_write_json(path: Path, payload: Any, compact: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        if compact:
            json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))
        else:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def detect_language(text: str) -> str:
    """Return en, el, neutral, or unsupported using Unicode scripts."""
    greek = len(GREEK_CHAR_RE.findall(text))
    latin = len(LATIN_CHAR_RE.findall(text))
    other = sum(
        1 for char in text
        if char.isalpha()
        and not GREEK_CHAR_RE.match(char)
        and not LATIN_CHAR_RE.match(char)
    )
    total = greek + latin + other
    if total == 0:
        return "neutral"
    if other and (other >= 2 or other / total > 0.12):
        return "unsupported"
    if greek >= 2 and greek >= latin * 0.22:
        return "el"
    if latin:
        return "en"
    if greek:
        return "el"
    return "unsupported"


def normalize_text(text: str) -> str:
    # Accent-insensitive matching is especially useful for Greek phone keyboards.
    decomposed = unicodedata.normalize("NFKD", text).casefold().replace("’", "'")
    decomposed = "".join(char for char in decomposed if not unicodedata.combining(char))
    decomposed = decomposed.replace("ς", "σ")
    return SPACE_RE.sub(" ", decomposed).strip()


def word_tokens(text: str) -> List[str]:
    return WORD_RE.findall(normalize_text(text))


def light_stem(token: str) -> str:
    """Conservative English/Greek suffix stripping for local retrieval."""
    if len(token) < 5:
        return token
    if GREEK_CHAR_RE.search(token):
        suffixes = (
            "οτητων", "ησεων", "ηματα", "οντας", "ουμε", "ουνε", "ηδες",
            "ικους", "ικες", "ικων", "ικο", "ικη", "ικα", "ους", "ων",
            "εις", "ετε", "εται", "ηση", "ησε", "ματα", "δες", "ες",
            "ος", "ης", "ας", "ου", "ει", "ουν", "ια", "ιο", "η", "α", "ο"
        )
        for suffix in suffixes:
            if token.endswith(suffix) and len(token) - len(suffix) >= 4:
                return token[:-len(suffix)]
        return token
    suffixes = (
        "ization", "ational", "fulness", "ousness", "iveness", "tional",
        "ments", "ment", "ingly", "edly", "ation", "ions", "tion",
        "ness", "able", "ible", "ing", "ers", "ies", "ied", "ed", "es", "s"
    )
    for suffix in suffixes:
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            root = token[:-len(suffix)]
            if suffix in {"ies", "ied"}:
                root += "y"
            return root
    return token


def token_variants(token: str) -> List[str]:
    variants = [token]
    stem = light_stem(token)
    if stem != token:
        variants.append("stem_" + stem)
    concept = CONCEPT_ALIASES.get(token) or CONCEPT_ALIASES.get(stem)
    if concept:
        variants.append(concept)
    return variants


def retrieval_terms(text: str) -> List[str]:
    terms: List[str] = []
    for token in word_tokens(text):
        if len(token) <= 1 or token in STOPWORDS:
            continue
        terms.extend(value[:64] for value in token_variants(token))
    return terms


def stable_hash(text: str, modulo: int) -> int:
    return (zlib.crc32(text.encode("utf-8")) & 0xFFFFFFFF) % modulo


def tokenize_features(text: str) -> List[str]:
    """Create bilingual word, stem, concept, subword, and local-order features."""
    words = word_tokens(text)[:180]
    features: List[str] = []
    previous_primary: List[str] = []
    for index, word in enumerate(words):
        variants = token_variants(word)
        for variant in variants:
            features.append("w=" + variant)
        if len(word) >= 3:
            features.append("p3=" + word[:3])
            features.append("s3=" + word[-3:])
        if len(word) >= 5:
            padded = "^" + word + "$"
            for begin in range(min(len(padded) - 2, 10)):
                features.append("c3=" + padded[begin:begin + 3])
        if previous_primary:
            features.append("b=" + previous_primary[-1] + "::" + word)
        if len(previous_primary) >= 2:
            features.append("t=" + previous_primary[-2] + "::" + previous_primary[-1] + "::" + word)
        previous_primary.append(word)
    language = detect_language(text)
    features.append("language=" + language)
    features.append("len=" + str(min(16, len(words))))
    if text.rstrip().endswith("?"):
        features.append("punct=question")
    if text.rstrip().endswith("!"):
        features.append("punct=exclaim")
    return features


def localized_intent_responses(intent: dict, language: str) -> List[str]:
    if language == "el":
        responses = GREEK_RESPONSES.get(str(intent.get("tag", "")), [])
        if responses:
            return responses
        greek = [value for value in intent.get("responses", []) if detect_language(str(value)) == "el"]
        return greek or FALLBACK_RESPONSES["el"]
    english = [value for value in intent.get("responses", []) if detect_language(str(value)) != "el"]
    return english or FALLBACK_RESPONSES["en"]

def hashed_sparse_vector(text: str, hash_size: int) -> Tuple[List[Tuple[int, float]], float]:
    features = tokenize_features(text)
    if not features:
        return [], 0.0
    counts: Counter[int] = Counter(stable_hash(feature, hash_size) for feature in features)
    norm = math.sqrt(sum(value * value for value in counts.values())) or 1.0
    vector = sorted((index, value / norm) for index, value in counts.items())
    return vector, min(1.0, len(features) / 18.0)


def validate_dataset(raw: Any) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("The dataset root must be a JSON object.")
    intents = raw.get("intents")
    if not isinstance(intents, list) or len(intents) < 2:
        raise ValueError("The dataset needs at least two intents.")

    clean_intents = []
    seen_tags = set()
    for item in intents:
        if not isinstance(item, dict):
            raise ValueError("Every intent must be an object.")
        tag = str(item.get("tag", "")).strip()
        patterns = item.get("patterns")
        responses = item.get("responses")
        if not tag or tag in seen_tags:
            raise ValueError(f"Intent tags must be non-empty and unique: {tag!r}")
        if not isinstance(patterns, list) or not any(str(value).strip() for value in patterns):
            raise ValueError(f"Intent {tag!r} has no usable patterns.")
        if not isinstance(responses, list) or not any(str(value).strip() for value in responses):
            raise ValueError(f"Intent {tag!r} has no usable responses.")
        seen_tags.add(tag)
        clean_patterns = [str(value).strip() for value in patterns if str(value).strip()]
        clean_responses = [str(value).strip() for value in responses if str(value).strip()]
        unsupported = [value for value in (*clean_patterns, *clean_responses) if detect_language(value) == "unsupported"]
        if unsupported:
            raise ValueError(f"Intent {tag!r} contains text outside English and Greek.")
        clean_intents.append({
            "tag": tag,
            "patterns": clean_patterns,
            "responses": clean_responses
        })

    fallbacks = raw.get("fallback_responses")
    if not isinstance(fallbacks, list) or not any(str(value).strip() for value in fallbacks):
        fallbacks = DEFAULT_DATASET["fallback_responses"]

    return {
        "dataset_version": int(raw.get("dataset_version", 1)),
        "assistant_name": str(raw.get("assistant_name", APP_NAME)).strip() or APP_NAME,
        "language": str(raw.get("language", "English and Greek only")),
        "fallback_responses": [str(value).strip() for value in fallbacks if str(value).strip()],
        "intents": clean_intents
    }


def ensure_dataset(path: Path) -> None:
    if not path.exists():
        atomic_write_json(path, DEFAULT_DATASET)


def available_memory_bytes() -> int:
    try:
        values: Dict[str, int] = {}
        with Path("/proc/meminfo").open("r", encoding="utf-8") as handle:
            for line in handle:
                key, value = line.split(":", 1)
                values[key] = int(value.strip().split()[0]) * 1024
        return values.get("MemAvailable", values.get("MemTotal", 0))
    except (OSError, ValueError, IndexError):
        return 0


def total_memory_bytes() -> int:
    try:
        with Path("/proc/meminfo").open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("MemTotal:"):
                    return int(line.split()[1]) * 1024
    except (OSError, ValueError, IndexError):
        pass
    return 0


def choose_auto_profile() -> str:
    total = total_memory_bytes()
    if total and total < 1_800_000_000:
        return "lite"
    if total and total < 2_700_000_000:
        return "balanced"
    if total and total < 4_500_000_000:
        return "max"
    return "extreme" if total else "max"




def _read_text_file(path: Path, limit: int = 65536) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit].strip()
    except OSError:
        return ""


def _android_property(name: str) -> str:
    # Environment overrides make the detector testable without Android and are
    # useful for advanced Termux users with unusual vendor properties.
    override = os.environ.get("POCKETAI_PROP_" + name.upper().replace(".", "_").replace("-", "_"))
    if override is not None:
        return override.strip()
    try:
        completed = subprocess.run(
            ["getprop", name], stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, errors="replace", timeout=2, check=False,
        )
        return completed.stdout.strip() if completed.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def _cpu_frequency_snapshot() -> dict:
    values: List[int] = []
    per_core: Dict[str, int] = {}
    roots = list(Path("/sys/devices/system/cpu").glob("cpu[0-9]*/cpufreq"))
    for root in roots:
        raw = ""
        for name in ("cpuinfo_max_freq", "scaling_max_freq"):
            raw = _read_text_file(root / name, 64)
            if raw:
                break
        try:
            khz = int(raw)
        except (TypeError, ValueError):
            continue
        if khz > 0:
            values.append(khz)
            per_core[root.parent.name] = khz
    distinct = sorted(set(values))
    return {
        "maximum_khz": max(values) if values else 0,
        "minimum_khz": min(values) if values else 0,
        "clusters_khz": distinct,
        "per_core_khz": per_core,
    }


def _storage_snapshot(path: Path) -> dict:
    try:
        path.mkdir(parents=True, exist_ok=True)
        usage = shutil.disk_usage(path)
        return {"path": str(path), "total": usage.total, "used": usage.used, "free": usage.free}
    except OSError:
        return {"path": str(path), "total": 0, "used": 0, "free": 0}


def _quick_processor_benchmark() -> dict:
    # Fixed, short standard-library workload. It is not a synthetic benchmark
    # leaderboard; it only separates very slow, entry, mid, and fast devices.
    rounds = 90000
    value = 0x12345678
    started = time.perf_counter()
    for index in range(rounds):
        value = ((value * 1664525 + 1013904223 + index) ^ (value >> 11)) & 0xFFFFFFFF
    integer_seconds = max(time.perf_counter() - started, 1e-6)

    float_rounds = 28000
    number = 0.125
    started = time.perf_counter()
    for index in range(float_rounds):
        number = (number * 1.000003 + (index % 17) * 0.00001) % 97.0
    float_seconds = max(time.perf_counter() - started, 1e-6)

    integer_rate = rounds / integer_seconds
    float_rate = float_rounds / float_seconds
    # Roughly normalized for CPython on Android. The final selector combines
    # this with chipset family, frequencies, architecture, and core topology.
    score = int(max(5, min(100, 16 + integer_rate / 55000 + float_rate / 23000)))
    return {
        "integer_ops_per_second": int(integer_rate),
        "float_ops_per_second": int(float_rate),
        "score": score,
        "checksum": int(value ^ int(number * 1000000)),
    }


def _detect_processor_family(search_text: str) -> dict:
    normalized = search_text.casefold()
    for pattern, vendor, family, tier_score in PROCESSOR_FAMILY_RULES:
        if re.search(pattern, normalized, re.IGNORECASE):
            return {"vendor": vendor, "family": family, "known_score": tier_score, "matched_pattern": pattern}
    machine = platform.machine() or "unknown"
    vendor = "Generic ARM" if "arm" in machine.casefold() or "aarch" in machine.casefold() else "Generic"
    return {"vendor": vendor, "family": f"Unknown {machine} processor", "known_score": 0, "matched_pattern": ""}


def _derive_cpu_score(family: dict, benchmark: dict, cpu_count: int, max_khz: int, is_64_bit: bool) -> int:
    known = int(family.get("known_score", 0) or 0)
    bench = int(benchmark.get("score", 0) or 0)
    core_component = min(14, max(0, cpu_count - 2) * 2)
    frequency_ghz = max_khz / 1_000_000 if max_khz else 0.0
    frequency_component = int(max(0.0, min(14.0, (frequency_ghz - 1.0) * 8.0)))
    architecture_component = 7 if is_64_bit else -9
    if known:
        combined = known * 0.62 + bench * 0.23 + core_component + frequency_component * 0.45 + architecture_component
    else:
        combined = bench * 0.72 + core_component + frequency_component + architecture_component
    return int(max(1, min(100, round(combined))))


def _model_path_status(script_dir: Path) -> dict:
    result: Dict[str, dict] = {}
    for model_id, config in EXTERNAL_LLM_MODELS.items():
        path = script_dir / "Models" / str(config["filename"])
        exists = path.is_file()
        result[model_id] = {
            "path": str(path),
            "exists": exists,
            "size": path.stat().st_size if exists else 0,
            "expected_sha256": str(config["sha256"]),
        }
    return result


def _check_model_compatibility(model_id: str, scan: dict) -> Tuple[bool, List[str]]:
    rules = AI_MODEL_COMPATIBILITY[model_id]
    reasons: List[str] = []
    if scan["ram"]["total"] < int(rules["minimum_total_ram"]):
        reasons.append("not enough total RAM")
    if scan["ram"]["available"] < int(rules["minimum_available_ram"]):
        reasons.append("not enough currently available RAM")
    if scan["storage"]["runtime"]["free"] < int(rules["minimum_free_storage"]):
        reasons.append("not enough free application storage")
    if scan["processor"]["score"] < int(rules["minimum_cpu_score"]):
        reasons.append("processor score is below the recommended range")
    if bool(rules["requires_64_bit"]) and not scan["processor"]["is_64_bit"]:
        reasons.append("64-bit userspace is required")
    if model_id in {"fast", "quality"} and not scan["models"][model_id]["exists"]:
        reasons.append("model file is missing")
    return not reasons, reasons


def _recommend_ai_configuration(scan: dict) -> dict:
    total = scan["ram"]["total"]
    available = scan["ram"]["available"]
    free = scan["storage"]["runtime"]["free"]
    score = scan["processor"]["score"]
    is_64 = scan["processor"]["is_64_bit"]

    compatibility: Dict[str, dict] = {}
    for model_id in AI_MODEL_COMPATIBILITY:
        compatible, reasons = _check_model_compatibility(model_id, scan)
        compatibility[model_id] = {"compatible": compatible, "reasons": reasons}

    if compatibility["quality"]["compatible"] and score >= 45 and available >= 650 * 1024 ** 2:
        gguf_model = "quality"
    elif compatibility["fast"]["compatible"]:
        gguf_model = "fast"
    else:
        gguf_model = "internal"

    if total < 900 * 1024 ** 2 or available < 150 * 1024 ** 2 or not is_64:
        runtime = "ultra_eco"
        classifier = "micro"
    elif total < 1550 * 1024 ** 2 or available < 290 * 1024 ** 2:
        runtime = "ultra_eco"
        classifier = "lite"
    elif total < 2400 * 1024 ** 2 or score < 22 or available < 480 * 1024 ** 2:
        runtime = "eco"
        classifier = "balanced"
    elif total < 3600 * 1024 ** 2 or score < 43 or available < 820 * 1024 ** 2:
        runtime = "entry"
        classifier = "standard"
    elif total < 5600 * 1024 ** 2 or score < 70:
        runtime = "balanced"
        classifier = "max"
    else:
        runtime = "performance"
        classifier = "max"

    # Every automatically selected classifier is bundled, preventing expensive
    # first-run training on old phones. Fall back through progressively smaller
    # pre-trained profiles if a file is damaged or manually removed.
    script_dir = Path(__file__).resolve().parent
    fallback_order = {
        "max": ("max", "standard", "balanced", "lite", "micro"),
        "standard": ("standard", "balanced", "lite", "micro"),
        "balanced": ("balanced", "lite", "micro"),
        "lite": ("lite", "micro"),
        "micro": ("micro",),
    }
    for candidate in fallback_order[classifier]:
        bundled = script_dir / "Models" / f"pretrained_{candidate}" / "neural_model.pkl.gz"
        if bundled.is_file():
            classifier = candidate
            break

    confidence = "high" if gguf_model != "internal" and score >= 35 else "medium" if is_64 else "safe fallback"
    return {
        "gguf_model": gguf_model,
        "classifier_profile": classifier,
        "runtime_profile": runtime,
        "llm_mode": "fallback" if gguf_model != "internal" else "off",
        "confidence": confidence,
        "compatibility": compatibility,
    }


def scan_phone_hardware(data_dir: Path, save: bool = True, run_benchmark: bool = True) -> dict:
    properties = {
        key: _android_property(prop)
        for key, prop in {
            "manufacturer": "ro.product.manufacturer",
            "brand": "ro.product.brand",
            "model": "ro.product.model",
            "device": "ro.product.device",
            "board": "ro.product.board",
            "hardware": "ro.hardware",
            "soc_model": "ro.soc.model",
            "soc_manufacturer": "ro.soc.manufacturer",
            "abi": "ro.product.cpu.abi",
            "abilist": "ro.product.cpu.abilist",
            "android_release": "ro.build.version.release",
            "android_sdk": "ro.build.version.sdk",
        }.items()
    }
    cpuinfo = _read_text_file(Path("/proc/cpuinfo"), 96000)
    frequency = _cpu_frequency_snapshot()
    machine = platform.machine() or os.uname().machine
    abi_text = " ".join([properties.get("abi", ""), properties.get("abilist", ""), machine]).casefold()
    is_64_bit = any(marker in abi_text for marker in ("arm64", "aarch64", "x86_64", "riscv64")) and sys.maxsize > 2 ** 32
    search_text = " ".join(str(value) for value in properties.values()) + " " + cpuinfo + " " + machine
    family = _detect_processor_family(search_text)
    benchmark = _quick_processor_benchmark() if run_benchmark else {"score": 30, "integer_ops_per_second": 0, "float_ops_per_second": 0, "checksum": 0}
    cpu_count = max(1, os.cpu_count() or 1)
    cpu_score = _derive_cpu_score(family, benchmark, cpu_count, int(frequency["maximum_khz"]), is_64_bit)

    total_ram = total_memory_bytes()
    available_ram = available_memory_bytes()
    script_dir = Path(__file__).resolve().parent
    home_storage = _storage_snapshot(Path.home())
    runtime_storage = _storage_snapshot(data_dir)
    shared_path = Path.home() / "storage" / "downloads"
    shared_storage = _storage_snapshot(shared_path) if shared_path.exists() else {"path": str(shared_path), "total": 0, "used": 0, "free": 0}

    scan = {
        "schema_version": 1,
        "scanned_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "device": properties,
        "processor": {
            **family,
            "raw_soc": properties.get("soc_model") or properties.get("hardware") or properties.get("board") or "unknown",
            "machine": machine,
            "abi": properties.get("abi", ""),
            "abilist": properties.get("abilist", ""),
            "is_64_bit": is_64_bit,
            "logical_cores": cpu_count,
            "frequency": frequency,
            "benchmark": benchmark,
            "score": cpu_score,
        },
        "ram": {"total": total_ram, "available": available_ram, "used": max(0, total_ram - available_ram)},
        "storage": {"runtime": runtime_storage, "home": home_storage, "shared_downloads": shared_storage},
        "models": _model_path_status(script_dir),
        "profile_path": str(data_dir / "device_profile.json"),
    }
    scan["recommendation"] = _recommend_ai_configuration(scan)
    if save:
        data_dir.mkdir(parents=True, exist_ok=True)
        atomic_write_json(data_dir / "device_profile.json", scan)
    return scan


def load_device_profile(data_dir: Path) -> Optional[dict]:
    path = data_dir / "device_profile.json"
    if not path.is_file():
        return None
    try:
        profile = load_json(path)
        return profile if isinstance(profile, dict) and profile.get("schema_version") == 1 else None
    except (OSError, ValueError, json.JSONDecodeError):
        return None


def _compatibility_line(model_id: str, scan: dict) -> str:
    rules = AI_MODEL_COMPATIBILITY[model_id]
    status = scan["recommendation"]["compatibility"][model_id]
    label = str(rules["label"])
    verdict = "SUPPORTED" if status["compatible"] else "NOT RECOMMENDED"
    requirements = (
        f"RAM {human_size(int(rules['minimum_total_ram']))}+; free RAM {human_size(int(rules['minimum_available_ram']))}+; "
        f"storage {human_size(int(rules['minimum_free_storage']))}+; CPU score {rules['minimum_cpu_score']}+"
    )
    reason = "" if status["compatible"] else "; " + ", ".join(status["reasons"])
    return f"  {label}: {verdict}\n    {requirements}{reason}\n    {rules['processor_combos']}"


def print_phone_scan_report(scan: dict) -> None:
    device = scan["device"]
    processor = scan["processor"]
    recommendation = scan["recommendation"]
    width = terminal_width()
    print("\n" + "=" * width)
    print(" PHONE AI COMPATIBILITY SCAN ".center(width, "="))
    print("=" * width)
    print(f"Device: {device.get('manufacturer', '')} {device.get('model', '')}".strip())
    print(f"Android: {device.get('android_release') or 'unknown'} (SDK {device.get('android_sdk') or '?'})")
    print(f"Processor: {processor['vendor']} - {processor['family']}")
    print(f"Reported SoC: {processor['raw_soc']}")
    print(f"Architecture: {processor['machine']} / {processor.get('abilist') or processor.get('abi') or 'unknown'} / {'64-bit' if processor['is_64_bit'] else '32-bit'}")
    freq = processor["frequency"]
    max_ghz = freq["maximum_khz"] / 1_000_000 if freq["maximum_khz"] else 0
    print(f"CPU: {processor['logical_cores']} logical cores; {max_ghz:.2f} GHz reported maximum; score {processor['score']}/100")
    print(f"RAM: {human_size(scan['ram']['total'])} total; {human_size(scan['ram']['available'])} currently available")
    storage = scan["storage"]["runtime"]
    print(f"Application storage: {human_size(storage['free'])} free of {human_size(storage['total'])}")
    shared = scan["storage"]["shared_downloads"]
    if shared["total"]:
        print(f"Shared Downloads storage: {human_size(shared['free'])} free of {human_size(shared['total'])}")
    print("\nModel compatibility:")
    print(_compatibility_line("internal", scan))
    print(_compatibility_line("fast", scan))
    print(_compatibility_line("quality", scan))
    print("\nBest automatic match:")
    print(f"  AI model: {recommendation['gguf_model']}")
    print(f"  Neural classifier: {recommendation['classifier_profile']}")
    print(f"  CPU/RAM runtime: {recommendation['runtime_profile']}")
    print(f"  Local LLM mode: {recommendation['llm_mode']}")
    print(f"  Selection confidence: {recommendation['confidence']}")
    print(f"  Saved profile: {scan.get('profile_path', Path(default_data_dir()) / 'device_profile.json')}")
    print("=" * width)


def launcher_menu(data_dir: Path) -> Optional[dict]:
    while True:
        width = terminal_width()
        print("\n" + "=" * width)
        print(" POCKETAI AUTOMATIC MODEL MATCHER ".center(width, "="))
        print("=" * width)
        print("1. Scan Phone To Find Matching AI Model")
        print("2. Run Local AI")
        try:
            choice = input("\nSelect 1 or 2: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return None
        if choice == "1":
            print("\nScanning processor, architecture, RAM, available storage, and model compatibility...")
            scan = scan_phone_hardware(data_dir, save=True, run_benchmark=True)
            print_phone_scan_report(scan)
            continue
        if choice == "2":
            scan = load_device_profile(data_dir)
            if scan is None:
                print("\nNo saved scan was found. Running the hardware scan automatically...")
                scan = scan_phone_hardware(data_dir, save=True, run_benchmark=True)
                print_phone_scan_report(scan)
                return scan
            else:
                # Refresh volatile RAM/storage and recommendation while preserving
                # the previous processor benchmark for a fast launch.
                refreshed = scan_phone_hardware(data_dir, save=True, run_benchmark=False)
                old_benchmark = scan.get("processor", {}).get("benchmark")
                if isinstance(old_benchmark, dict) and old_benchmark.get("score"):
                    refreshed["processor"]["benchmark"] = old_benchmark
                    family = {key: refreshed["processor"].get(key) for key in ("vendor", "family", "known_score", "matched_pattern")}
                    refreshed["processor"]["score"] = _derive_cpu_score(
                        family, old_benchmark, refreshed["processor"]["logical_cores"],
                        refreshed["processor"]["frequency"]["maximum_khz"], refreshed["processor"]["is_64_bit"]
                    )
                    refreshed["recommendation"] = _recommend_ai_configuration(refreshed)
                    atomic_write_json(data_dir / "device_profile.json", refreshed)
                return refreshed
        print("Invalid option. Enter 1 or 2.")

def terminal_width(default: int = 78) -> int:
    try:
        return max(44, min(110, shutil.get_terminal_size((default, 24)).columns))
    except OSError:
        return default


def print_banner(profile_name: str) -> None:
    width = terminal_width()
    title = f" {APP_NAME} "
    print("=" * width)
    print(title.center(width))
    print("Offline neural + retrieval assistant".center(width))
    print(f"Profile: {profile_name}".center(width))
    print("=" * width)


# ---------------------------------------------------------------------------
# Sparse deep neural intent classifier
# ---------------------------------------------------------------------------


@dataclass
class ForwardPass:
    hidden1: List[float]
    hidden2: List[float]
    probabilities: List[float]


class DeepSparseClassifier:
    """A memory-efficient two-hidden-layer neural classifier."""

    def __init__(
        self,
        tags: Sequence[str],
        hash_size: int,
        hidden1: int,
        hidden2: int,
        seed: int = RANDOM_SEED
    ) -> None:
        if len(tags) < 2:
            raise ValueError("A classifier needs at least two tags.")
        self.tags = list(tags)
        self.hash_size = int(hash_size)
        self.hidden1_size = int(hidden1)
        self.hidden2_size = int(hidden2)
        self.output_size = len(self.tags)
        self.tag_to_index = {tag: index for index, tag in enumerate(self.tags)}
        rng = random.Random(seed)

        scale1 = math.sqrt(2.0 / max(1, self.hash_size))
        scale2 = math.sqrt(2.0 / max(1, self.hidden1_size))
        scale3 = math.sqrt(2.0 / max(1, self.hidden2_size))

        self.w1 = array("f", (
            rng.uniform(-scale1, scale1)
            for _ in range(self.hash_size * self.hidden1_size)
        ))
        self.b1 = array("f", [0.0]) * self.hidden1_size
        self.w2 = array("f", (
            rng.uniform(-scale2, scale2)
            for _ in range(self.hidden1_size * self.hidden2_size)
        ))
        self.b2 = array("f", [0.0]) * self.hidden2_size
        self.w3 = array("f", (
            rng.uniform(-scale3, scale3)
            for _ in range(self.hidden2_size * self.output_size)
        ))
        self.b3 = array("f", [0.0]) * self.output_size

    @staticmethod
    def _softmax(logits: Sequence[float]) -> List[float]:
        peak = max(logits)
        values = [math.exp(max(-60.0, min(60.0, value - peak))) for value in logits]
        total = sum(values) or 1.0
        return [value / total for value in values]

    @staticmethod
    def _argmax(values: Sequence[float]) -> int:
        return max(range(len(values)), key=values.__getitem__)

    def forward(self, vector: Sequence[Tuple[int, float]]) -> ForwardPass:
        h1 = [float(value) for value in self.b1]
        h1_size = self.hidden1_size
        for feature_index, feature_value in vector:
            base = feature_index * h1_size
            for j in range(h1_size):
                h1[j] += self.w1[base + j] * feature_value
        h1 = [math.tanh(value) for value in h1]

        h2 = [float(value) for value in self.b2]
        h2_size = self.hidden2_size
        for j, activation in enumerate(h1):
            base = j * h2_size
            for k in range(h2_size):
                h2[k] += self.w2[base + k] * activation
        h2 = [math.tanh(value) for value in h2]

        logits = [float(value) for value in self.b3]
        output_size = self.output_size
        for k, activation in enumerate(h2):
            base = k * output_size
            for output_index in range(output_size):
                logits[output_index] += self.w3[base + output_index] * activation
        return ForwardPass(h1, h2, self._softmax(logits))

    def predict(self, text: str) -> Tuple[str, float, float, List[Tuple[str, float]]]:
        vector, feature_coverage = hashed_sparse_vector(text, self.hash_size)
        if not vector:
            return self.tags[0], 0.0, 0.0, []
        probabilities = self.forward(vector).probabilities
        order = sorted(range(len(probabilities)), key=probabilities.__getitem__, reverse=True)
        best = order[0]
        top = [(self.tags[index], probabilities[index]) for index in order[:3]]
        return self.tags[best], probabilities[best], feature_coverage, top

    def train(
        self,
        train_examples: List[Tuple[List[Tuple[int, float]], int]],
        validation_examples: List[Tuple[List[Tuple[int, float]], int]],
        epochs: int,
        learning_rate: float,
        verbose: bool = True
    ) -> dict:
        if not train_examples:
            raise ValueError("No training examples were supplied.")

        rng = random.Random(RANDOM_SEED + 77)
        output_size = self.output_size
        h1_size = self.hidden1_size
        h2_size = self.hidden2_size
        label_smoothing = 0.018
        l2 = 0.000035
        best_validation = -1.0
        best_loss = float("inf")
        patience = 0
        best_state: Optional[Tuple[array, array, array, array, array, array]] = None
        started = time.perf_counter()

        def evaluate(examples: Sequence[Tuple[List[Tuple[int, float]], int]]) -> Tuple[float, float]:
            if not examples:
                return 0.0, 0.0
            loss = 0.0
            correct = 0
            for vector, target in examples:
                probabilities = self.forward(vector).probabilities
                loss -= math.log(max(probabilities[target], 1e-12))
                correct += int(self._argmax(probabilities) == target)
            return loss / len(examples), correct / len(examples)

        completed_epoch = 0
        for epoch in range(1, max(1, epochs) + 1):
            completed_epoch = epoch
            rng.shuffle(train_examples)
            lr = learning_rate / (1.0 + 0.010 * (epoch - 1))
            running_loss = 0.0
            running_correct = 0

            for vector, target in train_examples:
                state = self.forward(vector)
                probabilities = state.probabilities
                running_loss -= math.log(max(probabilities[target], 1e-12))
                running_correct += int(self._argmax(probabilities) == target)

                # Output gradient with slight label smoothing.
                target_other = label_smoothing / max(1, output_size - 1)
                g3 = [
                    probabilities[index] - (1.0 - label_smoothing if index == target else target_other)
                    for index in range(output_size)
                ]

                # Calculate hidden2 gradient before changing w3.
                g2 = [0.0] * h2_size
                for k in range(h2_size):
                    base = k * output_size
                    total = 0.0
                    for output_index in range(output_size):
                        total += self.w3[base + output_index] * g3[output_index]
                    g2[k] = total * (1.0 - state.hidden2[k] * state.hidden2[k])

                # Calculate hidden1 gradient before changing w2.
                g1 = [0.0] * h1_size
                for j in range(h1_size):
                    base = j * h2_size
                    total = 0.0
                    for k in range(h2_size):
                        total += self.w2[base + k] * g2[k]
                    g1[j] = total * (1.0 - state.hidden1[j] * state.hidden1[j])

                # Update output layer.
                for k, activation in enumerate(state.hidden2):
                    base = k * output_size
                    for output_index in range(output_size):
                        index = base + output_index
                        gradient = activation * g3[output_index] + l2 * self.w3[index]
                        self.w3[index] -= lr * max(-3.5, min(3.5, gradient))
                for output_index in range(output_size):
                    self.b3[output_index] -= lr * g3[output_index]

                # Update second hidden layer.
                for j, activation in enumerate(state.hidden1):
                    base = j * h2_size
                    for k in range(h2_size):
                        index = base + k
                        gradient = activation * g2[k] + l2 * self.w2[index]
                        self.w2[index] -= lr * max(-3.5, min(3.5, gradient))
                for k in range(h2_size):
                    self.b2[k] -= lr * g2[k]

                # Update sparse input rows only.
                for feature_index, feature_value in vector:
                    base = feature_index * h1_size
                    for j in range(h1_size):
                        index = base + j
                        gradient = feature_value * g1[j] + l2 * self.w1[index]
                        self.w1[index] -= lr * max(-3.5, min(3.5, gradient))
                for j in range(h1_size):
                    self.b1[j] -= lr * g1[j]

            train_loss = running_loss / len(train_examples)
            train_accuracy = running_correct / len(train_examples)
            validation_loss, validation_accuracy = evaluate(validation_examples)
            monitored_accuracy = validation_accuracy if validation_examples else train_accuracy
            monitored_loss = validation_loss if validation_examples else train_loss

            improved = (
                monitored_accuracy > best_validation + 0.002
                or (
                    abs(monitored_accuracy - best_validation) <= 0.002
                    and monitored_loss < best_loss - 0.002
                )
            )
            if improved:
                best_validation = monitored_accuracy
                best_loss = monitored_loss
                patience = 0
                best_state = (
                    array("f", self.w1), array("f", self.b1),
                    array("f", self.w2), array("f", self.b2),
                    array("f", self.w3), array("f", self.b3)
                )
            else:
                patience += 1

            report_every = max(1, epochs // 14)
            if verbose and (epoch == 1 or epoch == epochs or epoch % report_every == 0):
                validation_text = (
                    f" val={validation_accuracy * 100:5.1f}%" if validation_examples else ""
                )
                print(
                    f"\rEpoch {epoch:4d}/{epochs}  loss={train_loss:.4f} "
                    f"train={train_accuracy * 100:5.1f}%{validation_text}",
                    end="", flush=True
                )

            if epoch >= 35 and patience >= 24:
                break
            if train_accuracy >= 0.998 and monitored_accuracy >= 0.94 and monitored_loss < 0.09 and patience >= 10:
                break

        if best_state is not None:
            self.w1, self.b1, self.w2, self.b2, self.w3, self.b3 = best_state
        final_train_loss, final_train_accuracy = evaluate(train_examples)
        final_validation_loss, final_validation_accuracy = evaluate(validation_examples)
        if verbose:
            print()

        return {
            "epochs_completed": completed_epoch,
            "train_loss": final_train_loss,
            "train_accuracy": final_train_accuracy,
            "validation_loss": final_validation_loss,
            "validation_accuracy": final_validation_accuracy,
            "training_seconds": time.perf_counter() - started
        }

    def parameter_count(self) -> int:
        return (
            len(self.w1) + len(self.b1) + len(self.w2) + len(self.b2)
            + len(self.w3) + len(self.b3)
        )

    def state_dict(self) -> dict:
        return {
            "model_version": MODEL_VERSION,
            "tags": self.tags,
            "hash_size": self.hash_size,
            "hidden1": self.hidden1_size,
            "hidden2": self.hidden2_size,
            "w1": self.w1,
            "b1": self.b1,
            "w2": self.w2,
            "b2": self.b2,
            "w3": self.w3,
            "b3": self.b3
        }

    @classmethod
    def from_state_dict(cls, state: Any) -> "DeepSparseClassifier":
        if not isinstance(state, dict) or state.get("model_version") != MODEL_VERSION:
            raise ValueError("Incompatible model format. Retrain the model.")
        model = cls(
            tags=list(state["tags"]),
            hash_size=int(state["hash_size"]),
            hidden1=int(state["hidden1"]),
            hidden2=int(state["hidden2"])
        )
        for name in ("w1", "b1", "w2", "b2", "w3", "b3"):
            value = state[name]
            setattr(model, name, value if isinstance(value, array) else array("f", value))
        model.validate_shapes()
        return model

    def validate_shapes(self) -> None:
        expected = {
            "w1": self.hash_size * self.hidden1_size,
            "b1": self.hidden1_size,
            "w2": self.hidden1_size * self.hidden2_size,
            "b2": self.hidden2_size,
            "w3": self.hidden2_size * self.output_size,
            "b3": self.output_size
        }
        for name, size in expected.items():
            if len(getattr(self, name)) != size:
                raise ValueError(f"Corrupt model array {name}: expected {size} values.")


def save_model(path: Path, model: DeepSparseClassifier) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with gzip.open(temporary, "wb", compresslevel=5) as handle:
        pickle.dump(model.state_dict(), handle, protocol=5)
    temporary.replace(path)


def load_model(path: Path) -> DeepSparseClassifier:
    # Model files are created locally by this program. Do not replace one with an
    # untrusted pickle from another person.
    with gzip.open(path, "rb") as handle:
        return DeepSparseClassifier.from_state_dict(pickle.load(handle))


def prepare_examples(dataset: dict, model: DeepSparseClassifier) -> List[Tuple[List[Tuple[int, float]], int, str]]:
    examples: List[Tuple[List[Tuple[int, float]], int, str]] = []
    for intent in dataset["intents"]:
        target = model.tag_to_index[intent["tag"]]
        for pattern in intent["patterns"]:
            vector, _ = hashed_sparse_vector(pattern, model.hash_size)
            if vector:
                examples.append((vector, target, intent["tag"]))
    return examples


def stratified_split(
    examples: List[Tuple[List[Tuple[int, float]], int, str]],
    validation_ratio: float = 0.14
) -> Tuple[List[Tuple[List[Tuple[int, float]], int]], List[Tuple[List[Tuple[int, float]], int]]]:
    grouped: Dict[str, List[Tuple[List[Tuple[int, float]], int, str]]] = defaultdict(list)
    for example in examples:
        grouped[example[2]].append(example)
    rng = random.Random(RANDOM_SEED + 9)
    train: List[Tuple[List[Tuple[int, float]], int]] = []
    validation: List[Tuple[List[Tuple[int, float]], int]] = []
    for group in grouped.values():
        rng.shuffle(group)
        validation_count = 1 if len(group) >= 6 else 0
        validation_count = max(validation_count, int(len(group) * validation_ratio))
        for index, (vector, target, _) in enumerate(group):
            destination = validation if index < validation_count else train
            destination.append((vector, target))
    rng.shuffle(train)
    rng.shuffle(validation)
    return train, validation


def train_classifier(
    dataset_path: Path,
    model_path: Path,
    metadata_path: Path,
    profile_name: str,
    epochs_override: Optional[int] = None,
    verbose: bool = True
) -> Tuple[DeepSparseClassifier, dict, dict]:
    dataset = validate_dataset(load_json(dataset_path))
    profile = MODEL_PROFILES[profile_name]
    tags = sorted(intent["tag"] for intent in dataset["intents"])
    model = DeepSparseClassifier(
        tags=tags,
        hash_size=profile["hash_size"],
        hidden1=profile["hidden1"],
        hidden2=profile["hidden2"]
    )
    prepared = prepare_examples(dataset, model)
    training, validation = stratified_split(prepared)
    if verbose:
        print(
            f"Training {profile_name} model: {len(training)} training examples, "
            f"{len(validation)} validation examples, {model.parameter_count():,} parameters."
        )
    stats = model.train(
        training,
        validation,
        epochs=int(epochs_override or profile["epochs"]),
        learning_rate=float(profile["learning_rate"]),
        verbose=verbose
    )
    save_model(model_path, model)
    metadata = {
        "model_version": MODEL_VERSION,
        "created_at": now_iso(),
        "dataset_sha256": sha256_file(dataset_path),
        "profile": profile_name,
        "hash_size": model.hash_size,
        "hidden1": model.hidden1_size,
        "hidden2": model.hidden2_size,
        "intent_count": len(tags),
        "example_count": len(prepared),
        "training_examples": len(training),
        "validation_examples": len(validation),
        "parameter_count": model.parameter_count(),
        **stats
    }
    atomic_write_json(metadata_path, metadata)
    return model, dataset, metadata


def model_is_current(metadata_path: Path, dataset_path: Path, profile_name: str) -> bool:
    if not metadata_path.exists():
        return False
    try:
        metadata = load_json(metadata_path)
        return (
            metadata.get("model_version") == MODEL_VERSION
            and metadata.get("profile") == profile_name
            and metadata.get("dataset_sha256") == sha256_file(dataset_path)
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return False


# ---------------------------------------------------------------------------
# Persistent retrieval memory and document index
# ---------------------------------------------------------------------------


class KnowledgeStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(path), timeout=30.0)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA synchronous=NORMAL")
        self.connection.execute("PRAGMA temp_store=MEMORY")
        self._create_schema()

    def _create_schema(self) -> None:
        with self.connection:
            self.connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    response TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_items_kind ON items(kind);

                CREATE TABLE IF NOT EXISTS terms (
                    term TEXT NOT NULL,
                    item_id INTEGER NOT NULL,
                    frequency REAL NOT NULL DEFAULT 1.0,
                    PRIMARY KEY(term, item_id),
                    FOREIGN KEY(item_id) REFERENCES items(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_terms_item ON terms(item_id);

                CREATE TABLE IF NOT EXISTS memories (
                    key TEXT PRIMARY KEY COLLATE NOCASE,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    text TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_history_created ON history(created_at);

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    def close(self) -> None:
        self.connection.close()

    def add_item(self, kind: str, prompt: str, response: str, source: str = "") -> int:
        prompt = SPACE_RE.sub(" ", prompt).strip()
        response = SPACE_RE.sub(" ", response).strip()
        if not prompt or not response:
            raise ValueError("Knowledge prompt and response cannot be empty.")
        term_counts = Counter(retrieval_terms(prompt))
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO items(kind,prompt,response,source,created_at) VALUES(?,?,?,?,?)",
                (kind, prompt, response, source, now_iso())
            )
            item_id = int(cursor.lastrowid)
            self.connection.executemany(
                "INSERT OR REPLACE INTO terms(term,item_id,frequency) VALUES(?,?,?)",
                [(term, item_id, float(count)) for term, count in term_counts.items()]
            )
        return item_id

    def teach(self, question: str, answer: str) -> int:
        return self.add_item("qa", question, answer, "manual teaching")

    def add_document_chunk(self, chunk: str, source: str) -> int:
        title = f"Information from {Path(source).name}"
        return self.add_item("document", chunk, chunk, source or title)

    def retrieve_many(
        self,
        query: str,
        limit: int = 6,
        candidate_limit: int = 56,
        language: Optional[str] = None
    ) -> List[dict]:
        """Rank local Q&A and document chunks with IDF-weighted hybrid scoring."""
        query_normalized = normalize_text(query)
        query_terms = retrieval_terms(query)
        unique_terms = list(dict.fromkeys(query_terms))[:36]
        if not unique_terms:
            return []
        placeholders = ",".join("?" for _ in unique_terms)
        rows = self.connection.execute(
            f"""
            SELECT item_id, COUNT(*) AS matches, SUM(frequency) AS frequency_sum
            FROM terms
            WHERE term IN ({placeholders})
            GROUP BY item_id
            ORDER BY matches DESC, frequency_sum DESC
            LIMIT ?
            """,
            (*unique_terms, candidate_limit)
        ).fetchall()
        if not rows:
            return []

        total_items = int(self.connection.execute(
            "SELECT COUNT(*) AS value FROM items"
        ).fetchone()["value"] or 1)
        df_rows = self.connection.execute(
            f"SELECT term, COUNT(*) AS value FROM terms WHERE term IN ({placeholders}) GROUP BY term",
            tuple(unique_terms)
        ).fetchall()
        document_frequency = {str(row["term"]): int(row["value"]) for row in df_rows}
        idf = {
            term: math.log((total_items + 1.0) / (document_frequency.get(term, 0) + 0.5)) + 1.0
            for term in unique_terms
        }
        total_query_weight = sum(idf.values()) or 1.0
        query_set = set(unique_terms)
        ranked: List[dict] = []

        for row in rows:
            item = self.connection.execute(
                "SELECT id,kind,prompt,response,source FROM items WHERE id=?", (row["item_id"],)
            ).fetchone()
            if item is None:
                continue
            prompt_normalized = normalize_text(item["prompt"])
            prompt_counts = Counter(retrieval_terms(item["prompt"]))
            prompt_set = set(prompt_counts)
            common = query_set & prompt_set
            overlap = len(common)
            if not overlap:
                continue
            weighted_overlap = sum(idf.get(term, 1.0) for term in common)
            idf_coverage = weighted_overlap / total_query_weight
            prompt_weight = sum(idf.get(term, 1.0) for term in prompt_set) or 1.0
            weighted_prompt_coverage = weighted_overlap / prompt_weight
            jaccard = overlap / max(1, len(query_set | prompt_set))
            tf_score = sum(
                idf.get(term, 1.0) * (1.0 + math.log1p(prompt_counts.get(term, 0)))
                for term in common
            ) / (total_query_weight * 1.7)
            sequence = difflib.SequenceMatcher(None, query_normalized, prompt_normalized).ratio()
            substring_bonus = 0.11 if query_normalized in prompt_normalized or prompt_normalized in query_normalized else 0.0
            exact_bonus = 0.20 if query_normalized == prompt_normalized else 0.0
            kind_bonus = 0.055 if item["kind"] == "qa" else 0.0
            item_language = detect_language(str(item["response"]))
            language_bonus = 0.07 if language in SUPPORTED_LANGUAGES and item_language == language else 0.0
            if language in SUPPORTED_LANGUAGES and item_language in SUPPORTED_LANGUAGES and item_language != language:
                language_bonus -= 0.035
            score = (
                0.34 * idf_coverage
                + 0.16 * weighted_prompt_coverage
                + 0.13 * jaccard
                + 0.13 * min(1.0, tf_score)
                + 0.24 * sequence
                + substring_bonus
                + exact_bonus
                + kind_bonus
                + language_bonus
            )
            ranked.append({
                "id": int(item["id"]),
                "kind": str(item["kind"]),
                "prompt": str(item["prompt"]),
                "response": str(item["response"]),
                "source": str(item["source"]),
                "score": min(1.0, max(0.0, score)),
                "overlap": overlap,
                "language": item_language,
                "idf_coverage": idf_coverage
            })
        ranked.sort(key=lambda candidate: (candidate["score"], candidate["overlap"]), reverse=True)
        return ranked[:max(1, limit)]

    def retrieve(self, query: str, limit: int = 28, language: Optional[str] = None) -> Optional[dict]:
        results = self.retrieve_many(query, limit=1, candidate_limit=max(28, limit), language=language)
        return results[0] if results else None

    def set_memory(self, key: str, value: str) -> None:
        key = key.strip()[:100]
        value = value.strip()[:4000]
        if not key or not value:
            raise ValueError("Memory key and value cannot be empty.")
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO memories(key,value,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
                """,
                (key, value, now_iso())
            )

    def get_memory(self, key: str) -> Optional[str]:
        row = self.connection.execute(
            "SELECT value FROM memories WHERE key=? COLLATE NOCASE", (key.strip(),)
        ).fetchone()
        return str(row["value"]) if row else None

    def list_memories(self, limit: int = 100) -> List[Tuple[str, str]]:
        rows = self.connection.execute(
            "SELECT key,value FROM memories ORDER BY key COLLATE NOCASE LIMIT ?", (limit,)
        ).fetchall()
        return [(str(row["key"]), str(row["value"])) for row in rows]

    def forget_memory(self, key: str) -> bool:
        with self.connection:
            cursor = self.connection.execute(
                "DELETE FROM memories WHERE key=? COLLATE NOCASE", (key.strip(),)
            )
        return cursor.rowcount > 0

    def add_history(self, role: str, text: str) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO history(role,text,created_at) VALUES(?,?,?)",
                (role, text[:MAX_INPUT_CHARS], now_iso())
            )
            self.connection.execute(
                """
                DELETE FROM history WHERE id NOT IN (
                    SELECT id FROM history ORDER BY id DESC LIMIT ?
                )
                """,
                (HISTORY_LIMIT,)
            )

    def recent_history(self, limit: int = 12) -> List[Tuple[str, str]]:
        rows = self.connection.execute(
            "SELECT role,text FROM history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [(str(row["role"]), str(row["text"])) for row in reversed(rows)]

    def clear_history(self) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM history")

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        row = self.connection.execute(
            "SELECT value FROM settings WHERE key=?", (key.strip(),)
        ).fetchone()
        return str(row["value"]) if row else default

    def set_setting(self, key: str, value: str) -> None:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO settings(key,value) VALUES(?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
                """,
                (key.strip(), value.strip())
            )

    def counts(self) -> dict:
        result = {}
        for kind in ("qa", "document"):
            row = self.connection.execute(
                "SELECT COUNT(*) AS value FROM items WHERE kind=?", (kind,)
            ).fetchone()
            result[kind] = int(row["value"])
        result["memories"] = int(
            self.connection.execute("SELECT COUNT(*) AS value FROM memories").fetchone()["value"]
        )
        result["history"] = int(
            self.connection.execute("SELECT COUNT(*) AS value FROM history").fetchone()["value"]
        )
        result["terms"] = int(
            self.connection.execute("SELECT COUNT(*) AS value FROM terms").fetchone()["value"]
        )
        return result

    def remove_source(self, source: str) -> int:
        ids = [
            int(row["id"]) for row in self.connection.execute(
                "SELECT id FROM items WHERE source=?", (source,)
            ).fetchall()
        ]
        if not ids:
            return 0
        with self.connection:
            self.connection.executemany("DELETE FROM terms WHERE item_id=?", [(value,) for value in ids])
            self.connection.executemany("DELETE FROM items WHERE id=?", [(value,) for value in ids])
        return len(ids)

    def export_json(self, path: Path) -> None:
        payload = {
            "exported_at": now_iso(),
            "items": [dict(row) for row in self.connection.execute(
                "SELECT kind,prompt,response,source,created_at FROM items ORDER BY id"
            )],
            "memories": [dict(row) for row in self.connection.execute(
                "SELECT key,value,updated_at FROM memories ORDER BY key"
            )]
        }
        atomic_write_json(path, payload)


# ---------------------------------------------------------------------------
# Document ingestion
# ---------------------------------------------------------------------------


def decode_text_bytes(data: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "utf-16", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def clean_document_text(text: str, suffix: str) -> str:
    if suffix in {".html", ".htm", ".xml"}:
        text = html.unescape(HTML_TAG_RE.sub(" ", text))
    text = text.replace("\x00", " ")
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def chunk_document(text: str, target_chars: int = 640, overlap_chars: int = 100) -> List[str]:
    text = text.strip()
    if not text:
        return []
    sentences = [segment.strip() for segment in SENTENCE_RE.split(text) if segment.strip()]
    if not sentences:
        sentences = [text]
    chunks: List[str] = []
    current = ""
    for sentence in sentences:
        if len(sentence) > target_chars * 2:
            pieces = [sentence[index:index + target_chars] for index in range(0, len(sentence), target_chars)]
        else:
            pieces = [sentence]
        for piece in pieces:
            candidate = f"{current} {piece}".strip()
            if current and len(candidate) > target_chars:
                chunks.append(current)
                tail = current[-overlap_chars:] if overlap_chars else ""
                current = f"{tail} {piece}".strip()
            else:
                current = candidate
    if current:
        chunks.append(current)
    return chunks[:MAX_DOCUMENT_CHUNKS_PER_FILE]


def iter_ingest_files(path: Path) -> Iterator[Path]:
    if path.is_file():
        yield path
        return
    count = 0
    for candidate in sorted(path.rglob("*")):
        if count >= MAX_INGEST_FILES:
            break
        if candidate.is_file() and candidate.suffix.casefold() in SUPPORTED_TEXT_SUFFIXES:
            count += 1
            yield candidate


def ingest_path(store: KnowledgeStore, path: Path, replace_existing: bool = True) -> dict:
    path = path.expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    files_seen = 0
    files_indexed = 0
    chunks_added = 0
    bytes_read = 0
    skipped: List[str] = []

    for file_path in iter_ingest_files(path):
        files_seen += 1
        try:
            size = file_path.stat().st_size
            if size <= 0 or size > MAX_FILE_BYTES:
                skipped.append(f"{file_path} ({human_size(size)})")
                continue
            raw = file_path.read_bytes()
            bytes_read += len(raw)
            text = clean_document_text(decode_text_bytes(raw), file_path.suffix.casefold())
            chunks = chunk_document(text)
            supported_chunks = [
                chunk for chunk in chunks
                if detect_language(chunk) in {"en", "el", "neutral"}
            ]
            if not supported_chunks:
                skipped.append(f"{file_path}: no English or Greek text")
                continue
            source = str(file_path)
            if replace_existing:
                store.remove_source(source)
            for chunk in supported_chunks:
                store.add_document_chunk(chunk, source)
                chunks_added += 1
            files_indexed += 1
        except (OSError, UnicodeError, sqlite3.Error) as error:
            skipped.append(f"{file_path}: {error}")

    return {
        "path": str(path),
        "files_seen": files_seen,
        "files_indexed": files_indexed,
        "chunks_added": chunks_added,
        "bytes_read": bytes_read,
        "skipped": skipped[:20]
    }


# ---------------------------------------------------------------------------
# Safe calculator
# ---------------------------------------------------------------------------


class SafeCalculator:
    BINARY = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow
    }
    UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}
    FUNCTIONS = {
        "abs": abs,
        "round": round,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "floor": math.floor,
        "ceil": math.ceil,
        "degrees": math.degrees,
        "radians": math.radians
    }
    CONSTANTS = {"pi": math.pi, "e": math.e, "tau": math.tau}

    def evaluate(self, expression: str) -> float:
        expression = expression.strip()
        if not expression or len(expression) > 400:
            raise ValueError("Expression is empty or too long.")
        tree = ast.parse(expression, mode="eval")
        result = self._evaluate_node(tree.body, depth=0)
        if isinstance(result, complex) or not math.isfinite(float(result)):
            raise ValueError("Result is not a finite real number.")
        return float(result)

    def _evaluate_node(self, node: ast.AST, depth: int) -> float:
        if depth > 30:
            raise ValueError("Expression is too deeply nested.")
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            value = float(node.value)
            if abs(value) > 1e100:
                raise ValueError("Numeric value is too large.")
            return value
        if isinstance(node, ast.Name) and node.id in self.CONSTANTS:
            return float(self.CONSTANTS[node.id])
        if isinstance(node, ast.UnaryOp) and type(node.op) in self.UNARY:
            return float(self.UNARY[type(node.op)](self._evaluate_node(node.operand, depth + 1)))
        if isinstance(node, ast.BinOp) and type(node.op) in self.BINARY:
            left = self._evaluate_node(node.left, depth + 1)
            right = self._evaluate_node(node.right, depth + 1)
            if isinstance(node.op, ast.Pow) and (abs(right) > 100 or abs(left) > 1e20):
                raise ValueError("Exponentiation is too large.")
            return float(self.BINARY[type(node.op)](left, right))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            function = self.FUNCTIONS.get(node.func.id)
            if function is None or node.keywords or len(node.args) > 3:
                raise ValueError("Function is not allowed.")
            arguments = [self._evaluate_node(arg, depth + 1) for arg in node.args]
            return float(function(*arguments))
        raise ValueError(f"Unsupported expression component: {type(node).__name__}")


# ---------------------------------------------------------------------------
# Experimental local n-gram language model
# ---------------------------------------------------------------------------


def surface_tokens(text: str) -> List[str]:
    return WORD_RE.findall(unicodedata.normalize("NFKC", text).casefold())


class NGramLanguageModel:
    def __init__(self, order: int = 3) -> None:
        self.order = max(2, min(4, int(order)))
        self.transitions: Dict[Tuple[str, ...], Counter[str]] = defaultdict(Counter)
        self.starts: List[Tuple[str, ...]] = []
        self.transitions_by_language: Dict[str, Dict[Tuple[str, ...], Counter[str]]] = {
            "en": defaultdict(Counter),
            "el": defaultdict(Counter)
        }
        self.starts_by_language: Dict[str, List[Tuple[str, ...]]] = {"en": [], "el": []}

    def train_texts(self, texts: Iterable[str]) -> int:
        sentence_count = 0
        for text in texts:
            for sentence in SENTENCE_RE.split(text):
                words = surface_tokens(sentence)
                if len(words) < self.order:
                    continue
                language = detect_language(sentence)
                if language not in SUPPORTED_LANGUAGES:
                    language = "en"
                padded = ["<s>"] * (self.order - 1) + words + ["</s>"]
                start_context = tuple(padded[:self.order - 1])
                self.starts.append(start_context)
                self.starts_by_language[language].append(start_context)
                language_map = self.transitions_by_language[language]
                for index in range(len(padded) - self.order + 1):
                    context = tuple(padded[index:index + self.order - 1])
                    next_word = padded[index + self.order - 1]
                    self.transitions[context][next_word] += 1
                    language_map[context][next_word] += 1
                sentence_count += 1
        return sentence_count

    def generate(self, prompt: str = "", max_words: int = 48, seed: Optional[int] = None) -> str:
        if not self.transitions:
            return "The local language model has not been built yet."
        rng = random.Random(seed if seed is not None else time.time_ns())
        language = detect_language(prompt)
        if language not in SUPPORTED_LANGUAGES:
            language = "en"
        transitions = self.transitions_by_language.get(language) or self.transitions
        starts = self.starts_by_language.get(language) or self.starts
        prompt_words = surface_tokens(prompt)
        if len(prompt_words) >= self.order - 1:
            context = tuple(prompt_words[-(self.order - 1):])
            if context not in transitions:
                context = rng.choice(starts)
        else:
            context = rng.choice(starts)

        output = [word for word in prompt_words[-8:] if word not in {"<s>", "</s>"}]
        for _ in range(max(1, max_words)):
            choices = transitions.get(context)
            if not choices:
                context = rng.choice(starts)
                choices = transitions.get(context)
                if not choices:
                    break
            population = list(choices.keys())
            weights = [max(1, count) ** 0.78 for count in choices.values()]
            next_word = rng.choices(population, weights=weights, k=1)[0]
            if next_word == "</s>":
                if len(output) >= 8:
                    break
                context = rng.choice(starts)
                continue
            output.append(next_word)
            context = tuple((*context[1:], next_word))
        if not output:
            return "No text was generated." if language == "en" else "Δεν δημιουργήθηκε κείμενο."
        result = " ".join(output)
        return result[0].upper() + result[1:] + ("" if result.endswith((".", "!", "?")) else ".")

    def save(self, path: Path) -> None:
        payload = {
            "version": 2,
            "order": self.order,
            "transitions": dict(self.transitions),
            "starts": self.starts,
            "transitions_by_language": {
                language: dict(mapping)
                for language, mapping in self.transitions_by_language.items()
            },
            "starts_by_language": self.starts_by_language
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        with gzip.open(temporary, "wb", compresslevel=6) as handle:
            pickle.dump(payload, handle, protocol=5)
        temporary.replace(path)

    @classmethod
    def load(cls, path: Path) -> "NGramLanguageModel":
        with gzip.open(path, "rb") as handle:
            payload = pickle.load(handle)
        model = cls(payload["order"])
        model.transitions = defaultdict(Counter, payload["transitions"])
        model.starts = list(payload["starts"])
        by_language = payload.get("transitions_by_language")
        starts_by_language = payload.get("starts_by_language")
        if isinstance(by_language, dict) and isinstance(starts_by_language, dict):
            model.transitions_by_language = {
                language: defaultdict(Counter, mapping)
                for language, mapping in by_language.items()
                if language in SUPPORTED_LANGUAGES
            }
            for language in SUPPORTED_LANGUAGES:
                model.transitions_by_language.setdefault(language, defaultdict(Counter))
            model.starts_by_language = {
                language: list(starts_by_language.get(language, []))
                for language in SUPPORTED_LANGUAGES
            }
        else:
            # Backward compatibility for older locally built files.
            model.transitions_by_language = {
                "en": defaultdict(Counter, payload["transitions"]),
                "el": defaultdict(Counter, payload["transitions"])
            }
            model.starts_by_language = {"en": list(payload["starts"]), "el": list(payload["starts"])}
        return model


# ---------------------------------------------------------------------------
# Bilingual reasoning helpers
# ---------------------------------------------------------------------------


UNIT_ALIASES = {
    "m": "m", "meter": "m", "meters": "m", "metre": "m", "metres": "m", "μετρο": "m", "μετρα": "m",
    "km": "km", "kilometer": "km", "kilometers": "km", "kilometre": "km", "kilometres": "km", "χλμ": "km", "χιλιομετρο": "km", "χιλιομετρα": "km",
    "cm": "cm", "centimeter": "cm", "centimeters": "cm", "εκατοστο": "cm", "εκατοστα": "cm",
    "mm": "mm", "millimeter": "mm", "millimeters": "mm", "χιλιοστο": "mm", "χιλιοστα": "mm",
    "mi": "mi", "mile": "mi", "miles": "mi", "μιλι": "mi", "μιλια": "mi",
    "yd": "yd", "yard": "yd", "yards": "yd", "γιαρδα": "yd", "γιαρδες": "yd",
    "ft": "ft", "foot": "ft", "feet": "ft", "ποδι": "ft", "ποδια": "ft",
    "in": "in", "inch": "in", "inches": "in", "ιντσα": "in", "ιντσες": "in",
    "kg": "kg", "kilogram": "kg", "kilograms": "kg", "κιλο": "kg", "κιλα": "kg", "κιλογραμμο": "kg", "κιλογραμμα": "kg",
    "g": "g", "gram": "g", "grams": "g", "γραμμαριο": "g", "γραμμαρια": "g",
    "lb": "lb", "lbs": "lb", "pound": "lb", "pounds": "lb", "λιβρα": "lb", "λιβρες": "lb",
    "oz": "oz", "ounce": "oz", "ounces": "oz", "ουγγια": "oz", "ουγγιες": "oz",
    "b": "b", "byte": "b", "bytes": "b",
    "kb": "kb", "kilobyte": "kb", "kilobytes": "kb",
    "mb": "mb", "megabyte": "mb", "megabytes": "mb",
    "gb": "gb", "gigabyte": "gb", "gigabytes": "gb",
    "tb": "tb", "terabyte": "tb", "terabytes": "tb",
    "c": "c", "°c": "c", "celsius": "c", "κελσιου": "c",
    "f": "f", "°f": "f", "fahrenheit": "f", "φαρεναιτ": "f",
    "k": "k", "kelvin": "k", "κελβιν": "k"
}

UNIT_GROUPS = {
    "length": {"m": 1.0, "km": 1000.0, "cm": 0.01, "mm": 0.001, "mi": 1609.344, "yd": 0.9144, "ft": 0.3048, "in": 0.0254},
    "mass": {"kg": 1.0, "g": 0.001, "lb": 0.45359237, "oz": 0.028349523125},
    "storage": {"b": 1.0, "kb": 1024.0, "mb": 1024.0 ** 2, "gb": 1024.0 ** 3, "tb": 1024.0 ** 4}
}


def convert_units(value: float, source: str, target: str) -> float:
    source = UNIT_ALIASES.get(normalize_text(source), normalize_text(source))
    target = UNIT_ALIASES.get(normalize_text(target), normalize_text(target))
    if source in {"c", "f", "k"} or target in {"c", "f", "k"}:
        if source not in {"c", "f", "k"} or target not in {"c", "f", "k"}:
            raise ValueError("incompatible units")
        celsius = value if source == "c" else ((value - 32.0) * 5.0 / 9.0 if source == "f" else value - 273.15)
        return celsius if target == "c" else (celsius * 9.0 / 5.0 + 32.0 if target == "f" else celsius + 273.15)
    for group in UNIT_GROUPS.values():
        if source in group and target in group:
            return value * group[source] / group[target]
    raise ValueError("unknown or incompatible units")


def split_sentences(text: str) -> List[str]:
    sentences = [SPACE_RE.sub(" ", part).strip() for part in SENTENCE_RE.split(text)]
    return [sentence for sentence in sentences if len(sentence) >= 12]


def extractive_summary(text: str, language: str, max_sentences: int = 5) -> str:
    sentences = split_sentences(text)
    if not sentences:
        return text.strip()[:1200]
    if len(sentences) <= max_sentences:
        return " ".join(sentences)
    frequencies = Counter(
        term for term in retrieval_terms(text)
        if not term.startswith("concept_") and not term.startswith("stem_")
    )
    scored: List[Tuple[float, int, str]] = []
    for index, sentence in enumerate(sentences):
        terms = retrieval_terms(sentence)
        if not terms:
            continue
        unique = set(terms)
        content = sum(frequencies.get(term, 0) for term in unique) / math.sqrt(len(terms) + 1.0)
        position = 0.22 if index == 0 else 0.10 if index < 3 else 0.0
        length_penalty = 0.0 if 45 <= len(sentence) <= 360 else 0.08
        scored.append((content + position - length_penalty, index, sentence))
    chosen = sorted(sorted(scored, reverse=True)[:max_sentences], key=lambda item: item[1])
    summary = " ".join(item[2] for item in chosen)
    return summary[:1600]


def extractive_document_answer(query: str, candidates: Sequence[dict], language: str) -> str:
    query_terms = set(retrieval_terms(query))
    query_normalized = normalize_text(query)
    scored: List[Tuple[float, int, str, str]] = []
    serial = 0
    for candidate in candidates:
        if candidate.get("kind") != "document":
            continue
        for sentence in split_sentences(str(candidate.get("response", ""))):
            sentence_terms = set(retrieval_terms(sentence))
            overlap = len(query_terms & sentence_terms)
            if not overlap:
                continue
            coverage = overlap / max(1, len(query_terms))
            density = overlap / max(1, len(sentence_terms))
            sequence = difflib.SequenceMatcher(None, query_normalized, normalize_text(sentence)).ratio()
            language_bonus = 0.08 if detect_language(sentence) == language else 0.0
            score = 0.52 * coverage + 0.22 * density + 0.18 * sequence + 0.08 * float(candidate.get("score", 0.0)) + language_bonus
            scored.append((score, serial, sentence, str(candidate.get("source", ""))))
            serial += 1
    if not scored:
        return ""
    selected: List[Tuple[float, int, str, str]] = []
    normalized_seen: set = set()
    for item in sorted(scored, reverse=True):
        normalized = normalize_text(item[2])
        if normalized in normalized_seen:
            continue
        if any(difflib.SequenceMatcher(None, normalized, normalize_text(existing[2])).ratio() > 0.88 for existing in selected):
            continue
        selected.append(item)
        normalized_seen.add(normalized)
        if len(selected) >= 3:
            break
    selected.sort(key=lambda item: item[1])
    answer = " ".join(item[2] for item in selected)
    return answer[:1400]


def is_followup_message(text: str, language: str) -> bool:
    normalized = normalize_text(text)
    terms = word_tokens(text)
    if len(terms) > 9:
        return False
    if language == "el":
        exact = ("γιατί", "πως", "πώς", "περισσότερα", "συνέχισε")
        prefixes = ("εξήγησε περισσότερο", "τι γίνεται με", "και αυτό", "λεπτομέρειες για")
    else:
        exact = ("why", "how", "more", "continue")
        prefixes = ("explain more", "what about", "and that", "and it", "details about")
    if normalized in {normalize_text(value) for value in exact}:
        return True
    return any(normalized.startswith(normalize_text(value) + " ") for value in prefixes)



# ---------------------------------------------------------------------------
# Safe public-web research and optional GGUF language model
# ---------------------------------------------------------------------------


class _ReadableHTMLParser(HTMLParser):
    """Extract readable text while dropping scripts, styles, and navigation noise."""

    BLOCKED = {"script", "style", "noscript", "svg", "canvas", "template"}
    BREAKS = {"p", "div", "section", "article", "main", "header", "footer", "li", "br", "h1", "h2", "h3", "h4", "h5", "h6", "tr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: List[str] = []
        self.block_depth = 0

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        tag = tag.casefold()
        if tag in self.BLOCKED:
            self.block_depth += 1
        elif self.block_depth == 0 and tag in self.BREAKS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag in self.BLOCKED and self.block_depth:
            self.block_depth -= 1
        elif self.block_depth == 0 and tag in self.BREAKS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.block_depth == 0 and data.strip():
            self.parts.append(data)

    def text(self) -> str:
        value = html.unescape(" ".join(self.parts))
        value = re.sub(r"[ \t\r\f\v]+", " ", value)
        value = re.sub(r"\n\s*\n+", "\n\n", value)
        return value.strip()


DANGEROUS_DORK_PATTERNS = [
    re.compile(r"(?i)intitle\s*:\s*[\"']?index\s+of"),
    re.compile(r"(?i)inurl\s*:\s*(?:admin|login|signin|wp-admin|phpmyadmin|cgi-bin|dashboard)"),
    re.compile(r"(?i)(?:filetype|ext)\s*:\s*(?:env|sql|db|sqlite|bak|backup|pem|key|p12|pfx|kdbx|log|cfg|conf|ini)\b"),
    re.compile(r"(?i)(?:password|passwd|credentials?|api[_ -]?key|private[_ -]?key|secret|access[_ -]?token)\s*(?:=|:|filetype|ext)"),
    re.compile(r"(?i)(?:inurl|intitle|site)\s*:[^\s]*(?:webcam|camera|router|dvr|nvr|printer)"),
    re.compile(r"(?i)(?:php\?id=|/etc/passwd|BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY|jdbc:|mongodb://|postgres://)"),
]

SAFE_DORK_OPERATORS = {"site", "filetype", "intitle", "inurl", "before", "after"}


def validate_research_query(query: str) -> str:
    query = SPACE_RE.sub(" ", query.strip())[:500]
    if len(query) < 3:
        raise ValueError("Research query is too short.")
    if detect_language(query) == "unsupported":
        raise ValueError("Only English and Greek research queries are supported.")
    for pattern in DANGEROUS_DORK_PATTERNS:
        if pattern.search(query):
            raise ValueError(
                "This dork is blocked because it targets credentials, private files, "
                "admin interfaces, or exposed systems. Use public documentation research instead."
            )
    operators = re.findall(r"(?i)([a-z]+)\s*:", query)
    unsupported = sorted({operator.casefold() for operator in operators} - SAFE_DORK_OPERATORS)
    if unsupported:
        raise ValueError("Unsupported search operator(s): " + ", ".join(unsupported))
    return query


def _is_public_host(hostname: str) -> bool:
    hostname = hostname.strip(".[]").casefold()
    if not hostname or hostname in {"localhost", "localhost.localdomain"}:
        return False
    if hostname.endswith((".local", ".internal", ".lan", ".home", ".onion")):
        return False
    try:
        addresses = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return False
    for address in addresses:
        raw = address[4][0].split("%", 1)[0]
        try:
            ip = ipaddress.ip_address(raw)
        except ValueError:
            return False
        if not ip.is_global:
            return False
    return bool(addresses)


def validate_public_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only public HTTP and HTTPS URLs are allowed.")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not allowed.")
    if parsed.port not in {None, 80, 443}:
        raise ValueError("Non-standard network ports are not allowed.")
    if not _is_public_host(parsed.hostname):
        raise ValueError("Local, private, or non-public hosts are blocked.")
    suffix = Path(urllib.parse.unquote(parsed.path)).suffix.casefold()
    blocked_suffixes = {
        ".exe", ".apk", ".bin", ".iso", ".img", ".dmg", ".msi", ".deb", ".rpm",
        ".zip", ".rar", ".7z", ".tar", ".gz", ".xz", ".sql", ".db", ".sqlite",
        ".pem", ".key", ".p12", ".pfx", ".kdbx"
    }
    if suffix in blocked_suffixes:
        raise ValueError("Binary archives, executables, databases, and key files are not fetched.")
    return urllib.parse.urlunsplit(parsed)


class SafeWebResearch:
    """Search and index public English/Greek pages with conservative limits."""

    def __init__(self, store: KnowledgeStore) -> None:
        self.store = store
        self.last_request_time = 0.0

    def _request(self, url: str, timeout: int, accept: str) -> Tuple[bytes, str, str]:
        delay = WEB_DELAY_SECONDS - (time.monotonic() - self.last_request_time)
        if delay > 0:
            time.sleep(delay)
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": WEB_USER_AGENT,
                "Accept": accept,
                "Accept-Language": "en,el;q=0.9",
                "Cache-Control": "no-cache"
            }
        )
        self.last_request_time = time.monotonic()
        with urllib.request.urlopen(request, timeout=timeout) as response:
            final_url = response.geturl()
            if url.startswith(("http://", "https://")):
                validate_public_url(final_url)
            content_type = response.headers.get_content_type().casefold()
            declared = response.headers.get("Content-Length")
            if declared and int(declared) > WEB_MAX_DOWNLOAD_BYTES:
                raise ValueError("Remote page is larger than the download limit.")
            data = response.read(WEB_MAX_DOWNLOAD_BYTES + 1)
            if len(data) > WEB_MAX_DOWNLOAD_BYTES:
                raise ValueError("Remote page exceeded the download limit.")
            charset = response.headers.get_content_charset() or "utf-8"
            return data, content_type, charset

    def search(self, query: str, limit: int = 6) -> List[dict]:
        query = validate_research_query(query)
        limit = max(1, min(WEB_MAX_RESULTS, int(limit)))
        params = urllib.parse.urlencode({"q": query, "format": "rss", "count": str(limit)})
        url = "https://www.bing.com/search?" + params
        data, content_type, _ = self._request(
            url, WEB_SEARCH_TIMEOUT, "application/rss+xml, application/xml, text/xml;q=0.9"
        )
        if content_type not in {"application/rss+xml", "application/xml", "text/xml", "text/plain"}:
            raise ValueError(f"Search provider returned unsupported content type: {content_type}")
        try:
            root = ET.fromstring(data)
        except ET.ParseError as error:
            raise ValueError(f"Search results could not be parsed: {error}") from error
        results: List[dict] = []
        seen: set = set()
        for item in root.findall(".//item"):
            title = html.unescape((item.findtext("title") or "").strip())
            link = html.unescape((item.findtext("link") or "").strip())
            description = html.unescape(HTML_TAG_RE.sub(" ", item.findtext("description") or ""))
            description = SPACE_RE.sub(" ", description).strip()
            if not title or not link or link in seen:
                continue
            try:
                safe_link = validate_public_url(link)
            except ValueError:
                continue
            seen.add(safe_link)
            results.append({"title": title[:300], "url": safe_link, "snippet": description[:1200]})
            if len(results) >= limit:
                break
        return results

    @staticmethod
    def _robots_allowed(url: str) -> bool:
        parsed = urllib.parse.urlsplit(url)
        robots_url = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, "/robots.txt", "", ""))
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(robots_url)
        request = urllib.request.Request(robots_url, headers={"User-Agent": WEB_USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=6) as response:
                if response.status >= 400:
                    return True
                lines = decode_text_bytes(response.read(160 * 1024)).splitlines()
            parser.parse(lines)
            return parser.can_fetch(WEB_USER_AGENT, url)
        except urllib.error.HTTPError as error:
            return error.code in {404, 410}
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            # A network failure is not treated as an explicit robots disallow.
            return True

    def fetch_text(self, url: str) -> Tuple[str, str]:
        url = validate_public_url(url)
        if not self._robots_allowed(url):
            raise PermissionError("The site's robots.txt disallows this page.")
        data, content_type, charset = self._request(
            url, WEB_PAGE_TIMEOUT, "text/html, text/plain;q=0.9, application/xhtml+xml;q=0.8"
        )
        if content_type not in {"text/html", "application/xhtml+xml", "text/plain"}:
            raise ValueError(f"Skipped unsupported page type: {content_type}")
        try:
            decoded = data.decode(charset, errors="replace")
        except LookupError:
            decoded = data.decode("utf-8", errors="replace")
        if content_type == "text/plain":
            text = decoded
        else:
            parser = _ReadableHTMLParser()
            parser.feed(decoded)
            text = parser.text()
        text = clean_document_text(text, ".txt")
        if len(text) < 160:
            raise ValueError("The page did not contain enough readable text.")
        return text[:350000], url

    def learn(self, query: str, max_pages: int = 3) -> dict:
        query = validate_research_query(query)
        max_pages = max(0, min(WEB_MAX_PAGES_PER_RUN, int(max_pages)))
        results = self.search(query, limit=max(5, max_pages + 2))
        if not results:
            return {"query": query, "results": [], "pages": 0, "chunks": 0, "errors": []}

        chunks_added = 0
        pages = 0
        errors: List[str] = []
        for result in results:
            snippet = f"{result['title']}. {result['snippet']}".strip()
            if result["snippet"] and detect_language(snippet) in {"en", "el", "neutral"}:
                source = "web-search:" + result["url"]
                self.store.remove_source(source)
                for chunk in chunk_document(snippet, target_chars=650, overlap_chars=80):
                    if detect_language(chunk) in {"en", "el", "neutral"}:
                        self.store.add_document_chunk(chunk, source)
                        chunks_added += 1

        for result in results:
            if pages >= max_pages:
                break
            try:
                text, final_url = self.fetch_text(result["url"])
                page_chunks = [
                    chunk for chunk in chunk_document(text, target_chars=760, overlap_chars=110)
                    if detect_language(chunk) in {"en", "el", "neutral"}
                ][:160]
                if not page_chunks:
                    continue
                source = "web:" + final_url
                self.store.remove_source(source)
                for chunk in page_chunks:
                    self.store.add_document_chunk(chunk, source)
                chunks_added += len(page_chunks)
                pages += 1
            except (OSError, ValueError, PermissionError, TimeoutError, urllib.error.URLError) as error:
                errors.append(f"{result['url']}: {error}")

        return {
            "query": query,
            "results": results,
            "pages": pages,
            "chunks": chunks_added,
            "errors": errors[:8]
        }


class SpecialistModelRouter:
    """Load small bilingual task-specialist models from the bundled Models folder."""

    FILES = {
        "code": "PocketAI_Code_Specialist.json.gz",
        "math": "PocketAI_Math_Specialist.json.gz",
        "research": "PocketAI_Research_Specialist.json.gz",
    }

    def __init__(self, models_dir: Path) -> None:
        self.models_dir = models_dir
        self.models: Dict[str, dict] = {}
        for model_id, filename in self.FILES.items():
            path = models_dir / filename
            try:
                with gzip.open(path, "rt", encoding="utf-8") as handle:
                    payload = json.load(handle)
                if isinstance(payload, dict) and payload.get("id") == model_id:
                    payload["_path"] = str(path)
                    self.models[model_id] = payload
            except (OSError, ValueError, TypeError, json.JSONDecodeError):
                continue

    @staticmethod
    def _contains_weighted_term(normalized: str, terms: set, key: str) -> bool:
        needle = normalize_text(key)
        if not needle:
            return False
        if " " in needle:
            return needle in normalized
        return needle in terms or any(term.startswith(needle) for term in terms)

    def select(self, text: str) -> Optional[dict]:
        normalized = normalize_text(text)
        terms = set(retrieval_terms(text)) | set(word_tokens(normalized))
        ranked: List[Tuple[float, str, List[str]]] = []
        for model_id, model in self.models.items():
            score = 0.0
            matched: List[str] = []
            for key, weight in dict(model.get("weights", {})).items():
                if self._contains_weighted_term(normalized, terms, str(key)):
                    score += float(weight)
                    matched.append(str(key))
            for phrase, weight in dict(model.get("phrases", {})).items():
                if normalize_text(str(phrase)) in normalized:
                    score += float(weight)
                    matched.append(str(phrase))
            # Training patterns inside each specialist are also part of the
            # routing model, which is especially useful for inflected Greek.
            best_pattern_score = 0.0
            best_pattern = ""
            for item in model.get("knowledge", []):
                for pattern in item.get("patterns", []):
                    pattern_norm = normalize_text(str(pattern))
                    pattern_terms = set(retrieval_terms(str(pattern)))
                    overlap = len(terms & pattern_terms)
                    coverage = overlap / max(1, len(pattern_terms))
                    sequence = difflib.SequenceMatcher(None, normalized, pattern_norm).ratio()
                    candidate = 2.8 * coverage + 1.8 * sequence
                    if normalized == pattern_norm:
                        candidate += 3.0
                    elif pattern_norm in normalized or normalized in pattern_norm:
                        candidate += 1.2
                    if candidate > best_pattern_score:
                        best_pattern_score = candidate
                        best_pattern = str(pattern)
            if best_pattern_score >= 2.2:
                score += best_pattern_score
                matched.append(best_pattern)
            # Keep one generic keyword from routing every query to a specialist.
            if len(set(matched)) == 1:
                score *= 0.58
            ranked.append((score, model_id, matched))
        if not ranked:
            return None
        ranked.sort(reverse=True)
        score, model_id, matched = ranked[0]
        second = ranked[1][0] if len(ranked) > 1 else 0.0
        if score < 2.4 or score - second < 0.35:
            return None
        model = self.models[model_id]
        return {
            "id": model_id,
            "label": model.get("label", model_id),
            "score": score,
            "matched": matched,
            "prompt": model.get("prompt", {}),
            "path": model.get("_path", ""),
        }

    def knowledge_answer(self, text: str, language: str, selected: Optional[dict] = None) -> Optional[dict]:
        selected = selected or self.select(text)
        if not selected:
            return None
        model = self.models.get(str(selected["id"]))
        if not model:
            return None
        normalized = normalize_text(text)
        query_terms = set(retrieval_terms(text))
        best: Optional[Tuple[float, dict, str]] = None
        for item in model.get("knowledge", []):
            for pattern in item.get("patterns", []):
                pattern_text = str(pattern)
                pattern_norm = normalize_text(pattern_text)
                pattern_terms = set(retrieval_terms(pattern_text))
                overlap = len(query_terms & pattern_terms)
                coverage = overlap / max(1, len(pattern_terms))
                query_coverage = overlap / max(1, len(query_terms))
                sequence = difflib.SequenceMatcher(None, normalized, pattern_norm).ratio()
                exact_bonus = 0.28 if normalized == pattern_norm else 0.12 if pattern_norm in normalized or normalized in pattern_norm else 0.0
                score = 0.38 * coverage + 0.28 * query_coverage + 0.34 * sequence + exact_bonus
                if best is None or score > best[0]:
                    best = (score, item, pattern_text)
        if best is None or best[0] < 0.61:
            return None
        item = best[1]
        response = str(item.get(language) or item.get("en") or "").strip()
        if not response:
            return None
        return {
            "response": response,
            "specialist": selected,
            "match_score": min(1.0, best[0]),
            "pattern": best[2],
        }

    def instruction(self, selected: Optional[dict], language: str) -> str:
        if not selected:
            return ""
        prompt = selected.get("prompt", {})
        if isinstance(prompt, dict):
            return str(prompt.get(language) or prompt.get("en") or "").strip()
        return ""

    def status(self) -> List[dict]:
        result = []
        for model_id, filename in self.FILES.items():
            model = self.models.get(model_id)
            path = self.models_dir / filename
            result.append({
                "id": model_id,
                "label": model.get("label", model_id) if model else model_id,
                "path": str(path),
                "loaded": model is not None,
                "size": path.stat().st_size if path.is_file() else 0,
            })
        return result


class LocalGGUFModel:
    """llama.cpp bridge with RAM and processor presets for low-end Android."""

    def __init__(
        self,
        data_dir: Path,
        preferred_model: str = DEFAULT_EXTERNAL_LLM_MODEL,
        cpu_profile: str = DEFAULT_LLM_CPU_PROFILE,
    ) -> None:
        self.data_dir = data_dir
        self.script_dir = Path(__file__).resolve().parent
        self.binary_path = self._find_binary()
        self.model_paths: Dict[str, Path] = {}
        self.active_model = self._normalize_model_name(preferred_model)
        self.requested_cpu_profile = self._normalize_cpu_profile(cpu_profile)
        self.device_info = self._detect_device_info()
        self.resolved_cpu_profile = self._resolve_cpu_profile()
        self.refresh()

    @staticmethod
    def _normalize_model_name(name: str) -> str:
        aliases = {
            "q2": "fast", "q2_k": "fast", "low": "fast", "small": "fast",
            "ram": "fast", "speed": "fast", "1": "fast",
            "q4": "quality", "q4_1": "quality", "best": "quality",
            "smart": "quality", "2": "quality",
        }
        normalized = aliases.get(name.casefold().strip(), name.casefold().strip())
        return normalized if normalized in EXTERNAL_LLM_MODELS else DEFAULT_EXTERNAL_LLM_MODEL

    @staticmethod
    def _normalize_cpu_profile(name: str) -> str:
        aliases = {
            "automatic": "auto", "detect": "auto", "default": "auto",
            "minimum": "ultra_eco", "emergency": "ultra_eco", "tiny": "ultra_eco",
            "slow": "eco", "safe": "eco", "low": "eco", "1": "eco",
            "a12": "entry", "lowcpu": "entry", "low-cpu": "entry",
            "galaxy-a12": "entry", "galaxya12": "entry", "p35": "entry", "exynos850": "entry",
            "normal": "balanced", "standard": "balanced", "2": "entry", "3": "balanced",
            "fast": "performance", "strong": "performance", "4": "performance",
        }
        normalized = aliases.get(name.casefold().strip(), name.casefold().strip())
        if normalized == "auto" or normalized in LLM_CPU_PROFILES:
            return normalized
        raise ValueError("CPU profile must be auto, ultra_eco, eco, entry, balanced, or performance.")

    @staticmethod
    def _get_android_property(name: str) -> str:
        try:
            completed = subprocess.run(
                ["getprop", name],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                errors="replace",
                timeout=2,
                check=False,
            )
            return completed.stdout.strip() if completed.returncode == 0 else ""
        except (OSError, subprocess.SubprocessError):
            return ""

    @classmethod
    def _detect_device_info(cls) -> dict:
        data_dir = default_data_dir()
        try:
            scan = scan_phone_hardware(data_dir, save=False, run_benchmark=False)
            return {
                **scan.get("device", {}),
                "cpu_count": scan["processor"]["logical_cores"],
                "total_ram": scan["ram"]["total"],
                "available_ram": scan["ram"]["available"],
                "processor_score": scan["processor"]["score"],
                "processor_family": scan["processor"]["family"],
                "is_64_bit": scan["processor"]["is_64_bit"],
            }
        except Exception:
            return {
                "model": cls._get_android_property("ro.product.model"),
                "device": cls._get_android_property("ro.product.device"),
                "hardware": cls._get_android_property("ro.hardware"),
                "board": cls._get_android_property("ro.product.board"),
                "soc_model": cls._get_android_property("ro.soc.model"),
                "soc_manufacturer": cls._get_android_property("ro.soc.manufacturer"),
                "cpu_count": max(1, os.cpu_count() or 1),
                "total_ram": total_memory_bytes(),
                "available_ram": available_memory_bytes(),
                "processor_score": 30,
                "processor_family": "Unknown",
                "is_64_bit": sys.maxsize > 2 ** 32,
            }

    def _resolve_cpu_profile(self) -> str:
        if self.requested_cpu_profile != "auto":
            return self.requested_cpu_profile
        total = int(self.device_info.get("total_ram", 0) or 0)
        available = int(self.device_info.get("available_ram", 0) or 0)
        score = int(self.device_info.get("processor_score", 30) or 30)
        is_64 = bool(self.device_info.get("is_64_bit", True))
        if not is_64 or (total and total < 1_500_000_000) or (available and available < 280_000_000):
            return "ultra_eco"
        if (total and total < 2_200_000_000) or (available and available < 470_000_000) or score < 25:
            return "eco"
        if (total and total < 3_400_000_000) or score < 43:
            return "entry"
        if (total and total < 5_200_000_000) or score < 68:
            return "balanced"
        return "performance"

    def runtime_settings(self) -> dict:
        # Refresh available RAM before every generation. A12-class devices can lose
        # hundreds of MB when Android starts background services.
        available = available_memory_bytes()
        selected = self.resolved_cpu_profile
        if available and available < 230_000_000:
            selected = "ultra_eco"
        elif available and available < 420_000_000 and selected not in {"ultra_eco", "eco"}:
            selected = "eco"
        profile = LLM_CPU_PROFILES[selected]
        context = min(
            int(EXTERNAL_LLM_MODELS[self.active_model]["context"]),
            int(profile["context"][self.active_model]),
        )
        max_tokens = min(
            int(EXTERNAL_LLM_MODELS[self.active_model]["max_tokens"]),
            int(profile["max_tokens"][self.active_model]),
        )
        return {
            "requested": self.requested_cpu_profile,
            "resolved": selected,
            "threads": max(1, min(int(profile["threads"]), os.cpu_count() or 1)),
            "context": context,
            "batch": int(profile["batch"]),
            "ubatch": int(profile["ubatch"]),
            "max_tokens": max_tokens,
            "timeout": int(profile["timeout"]),
            "description": str(profile["description"]),
            "available_ram": available,
        }

    def set_cpu_profile(self, name: str) -> str:
        self.requested_cpu_profile = self._normalize_cpu_profile(name)
        self.device_info = self._detect_device_info()
        self.resolved_cpu_profile = self._resolve_cpu_profile()
        return self.requested_cpu_profile

    def _candidate_paths(self, filename: str) -> List[Path]:
        return [
            self.script_dir / "Models" / filename,
            Path.home() / filename,
        ]

    def _find_models(self) -> Dict[str, Path]:
        found: Dict[str, Path] = {}
        for key, config in EXTERNAL_LLM_MODELS.items():
            filename = str(config["filename"])
            for candidate in self._candidate_paths(filename):
                try:
                    if candidate.is_file() and candidate.stat().st_size > 50 * 1024 * 1024:
                        found[key] = candidate
                        break
                except OSError:
                    continue
        return found

    def _find_binary(self) -> Optional[Path]:
        override = os.environ.get("POCKETAI_LLAMA_CLI", "").strip()
        candidates: List[Path] = []
        if override:
            candidates.append(Path(override).expanduser())
        located = shutil.which("llama-cli") or shutil.which("llama")
        if located:
            candidates.append(Path(located))
        candidates.extend([
            self.data_dir / "llama.cpp" / "build" / "bin" / "llama-cli",
            Path.home() / "llama.cpp" / "build" / "bin" / "llama-cli",
        ])
        for candidate in candidates:
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return candidate
        return None

    def refresh(self) -> None:
        self.model_paths = self._find_models()
        self.binary_path = self._find_binary()
        if self.active_model not in self.model_paths and self.model_paths:
            self.active_model = "quality" if "quality" in self.model_paths else next(iter(self.model_paths))

    @property
    def model_path(self) -> Optional[Path]:
        return self.model_paths.get(self.active_model)

    @property
    def available(self) -> bool:
        return self.model_path is not None and self.binary_path is not None

    def set_model(self, name: str) -> str:
        normalized = self._normalize_model_name(name)
        self.refresh()
        if normalized not in self.model_paths:
            filename = EXTERNAL_LLM_MODELS[normalized]["filename"]
            raise ValueError(f"Model {normalized!r} is missing: {filename}")
        self.active_model = normalized
        return normalized

    def status(self) -> dict:
        self.refresh()
        runtime = self.runtime_settings()
        models: Dict[str, dict] = {}
        for key, config in EXTERNAL_LLM_MODELS.items():
            model_path = self.model_paths.get(key)
            size = model_path.stat().st_size if model_path else 0
            digest = ""
            if model_path:
                try:
                    digest = sha256_file(model_path)
                except OSError:
                    digest = ""
            models[key] = {
                "label": config["label"],
                "path": str(model_path) if model_path else "missing",
                "size": size,
                "sha256": digest,
                "verified": bool(digest) and digest == config["sha256"],
            }
        return {
            "available": self.available,
            "active_model": self.active_model,
            "active_path": str(self.model_path) if self.model_path else "missing",
            "models": models,
            "binary": str(self.binary_path) if self.binary_path else "missing",
            "cpu_profile_requested": self.requested_cpu_profile,
            "cpu_profile_resolved": runtime["resolved"],
            "runtime": runtime,
            "device": self.device_info,
            "low_ram_defaults": True,
        }

    @staticmethod
    def _clean_output(output: str, prompt: str) -> str:
        output = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", output)
        if "<|im_start|>assistant" in output:
            output = output.rsplit("<|im_start|>assistant", 1)[-1]
        output = output.split("<|im_end|>", 1)[0]
        if prompt and output.startswith(prompt):
            output = output[len(prompt):]
        kept: List[str] = []
        noisy = (
            "build:", "main:", "llama_", "llm_", "ggml_", "load_", "system_info:",
            "sampling:", "generate:", "common_init", "print_info:",
        )
        for line in output.splitlines():
            stripped = line.strip()
            if not stripped or stripped.casefold().startswith(noisy):
                continue
            kept.append(stripped)
        cleaned = "\n".join(kept).strip()
        cleaned = cleaned.replace("<|im_start|>", "").replace("<|im_end|>", "").strip()
        return cleaned[:3000]

    def generate(
        self,
        user_text: str,
        language: str,
        context: str = "",
        max_tokens: int = 160,
        specialist_instruction: str = "",
    ) -> str:
        self.refresh()
        model_path = self.model_path
        if not self.available or model_path is None or self.binary_path is None:
            raise RuntimeError("The selected GGUF model or llama.cpp executable is not installed.")

        runtime = self.runtime_settings()
        language_instruction = "Answer in Greek." if language == "el" else "Answer in English."
        context_limits = {"ultra_eco": 1200, "eco": 1800, "entry": 2400, "balanced": 3000, "performance": 3600}
        input_limits = {"ultra_eco": 650, "eco": 900, "entry": 1200, "balanced": 1450, "performance": 1700}
        context_limit = context_limits.get(runtime["resolved"], 2400)
        input_limit = input_limits.get(runtime["resolved"], 1200)
        context = context.strip()[:context_limit]
        system = (
            "You are PocketAI, a careful assistant running locally on a low-end Android phone. "
            "You may communicate only in English or Greek. "
            + language_instruction
            + " Be concise and accurate. Use supplied local context when relevant. "
              "Do not invent sources, current facts, commands, or security claims. "
              "If you do not know, clearly say so."
        )
        if specialist_instruction.strip():
            system += "\nTask-specialist guidance: " + specialist_instruction.strip()[:1200]
        user = user_text.strip()[:input_limit]
        if context:
            user = "Local context:\n" + context + "\n\nUser question:\n" + user
        prompt = (
            "<|im_start|>system\n" + system + "<|im_end|>\n"
            "<|im_start|>user\n" + user + "<|im_end|>\n"
            "<|im_start|>assistant\n"
        )

        token_limit = min(int(runtime["max_tokens"]), max(24, min(224, max_tokens)))
        common = [
            str(self.binary_path), "-m", str(model_path),
            "-c", str(runtime["context"]),
            "-b", str(runtime["batch"]),
            "-ub", str(runtime["ubatch"]),
            "-n", str(token_limit),
            "-t", str(runtime["threads"]),
            "--mmap", "--no-warmup", "--simple-io", "--no-conversation",
            "--temp", "0.22", "--top-p", "0.90", "--repeat-penalty", "1.12",
            "-p", prompt,
        ]
        attempts = [common[:1] + ["--no-display-prompt"] + common[1:], common]
        last_error = ""
        environment = os.environ.copy()
        environment["OMP_NUM_THREADS"] = str(runtime["threads"])
        environment["OPENBLAS_NUM_THREADS"] = "1"
        environment["MKL_NUM_THREADS"] = "1"
        for command in attempts:
            try:
                completed = subprocess.run(
                    command,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    errors="replace",
                    timeout=runtime["timeout"],
                    check=False,
                    env=environment,
                )
            except (OSError, subprocess.SubprocessError) as error:
                last_error = str(error)
                continue
            output = self._clean_output(completed.stdout, prompt)
            if completed.returncode == 0 and output:
                if detect_language(output) == "unsupported":
                    raise RuntimeError("The local model produced text outside English and Greek.")
                return output
            last_error = output or self._clean_output(completed.stderr, prompt) or f"llama.cpp returned code {completed.returncode}"
        raise RuntimeError(last_error or "Local model inference failed.")


# ---------------------------------------------------------------------------
# Assistant engine
# ---------------------------------------------------------------------------


class PocketAssistant:
    def __init__(
        self,
        data_dir: Path,
        dataset_path: Path,
        model_path: Path,
        metadata_path: Path,
        database_path: Path,
        language_model_path: Path,
        model: DeepSparseClassifier,
        dataset: dict,
        metadata: dict,
        profile_name: str,
        confidence_threshold: float
    ) -> None:
        self.data_dir = data_dir
        self.dataset_path = dataset_path
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.database_path = database_path
        self.language_model_path = language_model_path
        self.model = model
        self.dataset = dataset
        self.metadata = metadata
        self.profile_name = profile_name
        self.confidence_threshold = confidence_threshold
        self.store = KnowledgeStore(database_path)
        self.calculator = SafeCalculator()
        self.debug = False
        self.session_history: Deque[Tuple[str, str]] = deque(maxlen=18)
        self.intent_lookup = {item["tag"]: item for item in dataset["intents"]}
        self.pattern_index = self._build_pattern_index(dataset)
        self.intent_profiles, self.intent_idf = self._build_intent_profiles(dataset)
        self.rng = random.Random(time.time_ns())
        stored_mode = self.store.get_setting("language_mode", "auto") or "auto"
        self.language_mode = stored_mode if stored_mode in {"auto", "en", "el"} else "auto"
        stored_last = self.store.get_setting("last_language", "en") or "en"
        self.last_language = stored_last if stored_last in SUPPORTED_LANGUAGES else "en"
        self.last_user_query = ""
        self.last_details: dict = {}
        self.recent_responses: Deque[str] = deque(maxlen=10)
        self.language_model: Optional[NGramLanguageModel] = None
        models_dir = Path(__file__).resolve().parent / "Models"
        total_ram = total_memory_bytes()
        available_ram = available_memory_bytes()
        quality_micro = models_dir / "PocketAI_Bilingual_MicroLM_Quality.pkl.gz"
        lite_micro = models_dir / "PocketAI_Bilingual_MicroLM_Lite.pkl.gz"
        legacy_micro = models_dir / "PocketAI_Bilingual_MicroLM.pkl.gz"
        prefer_quality_micro = (
            total_ram >= 2_200 * 1024 ** 2
            and (not available_ram or available_ram >= 360 * 1024 ** 2)
            and quality_micro.is_file()
        )
        bundled_micro = quality_micro if prefer_quality_micro else lite_micro
        if not bundled_micro.is_file():
            bundled_micro = legacy_micro
        self.micro_model_variant = "quality" if bundled_micro == quality_micro else "lite"
        if not language_model_path.exists() and bundled_micro.is_file():
            try:
                language_model_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(bundled_micro, language_model_path)
            except OSError:
                pass
        if language_model_path.exists():
            try:
                self.language_model = NGramLanguageModel.load(language_model_path)
            except (OSError, ValueError, KeyError, TypeError, pickle.PickleError):
                self.language_model = None
        self.web_research = SafeWebResearch(self.store)
        self.specialists = SpecialistModelRouter(Path(__file__).resolve().parent / "Models")
        stored_llm_model = self.store.get_setting("llm_model", DEFAULT_EXTERNAL_LLM_MODEL) or DEFAULT_EXTERNAL_LLM_MODEL
        stored_cpu_profile = self.store.get_setting("llm_cpu_profile", DEFAULT_LLM_CPU_PROFILE) or DEFAULT_LLM_CPU_PROFILE
        self.local_llm = LocalGGUFModel(
            data_dir,
            preferred_model=stored_llm_model,
            cpu_profile=stored_cpu_profile,
        )
        stored_llm_mode = self.store.get_setting("llm_mode", "fallback") or "fallback"
        self.llm_mode = stored_llm_mode if stored_llm_mode in {"off", "fallback", "always"} else "fallback"

    @staticmethod
    def _build_pattern_index(dataset: dict) -> List[Tuple[str, str, set, set]]:
        index: List[Tuple[str, str, set, set]] = []
        for intent in dataset["intents"]:
            for pattern in intent["patterns"]:
                normalized = normalize_text(pattern)
                tokens = set(retrieval_terms(pattern))
                chars = {
                    normalized[position:position + 3]
                    for position in range(max(0, len(normalized) - 2))
                    if " " not in normalized[position:position + 3]
                }
                index.append((intent["tag"], normalized, tokens, chars))
        return index

    @staticmethod
    def _build_intent_profiles(dataset: dict) -> Tuple[Dict[str, Counter], Dict[str, float]]:
        profiles: Dict[str, Counter] = {}
        document_frequency: Counter = Counter()
        for intent in dataset["intents"]:
            profile: Counter = Counter()
            for pattern in intent["patterns"]:
                profile.update(set(retrieval_terms(pattern)))
            profiles[str(intent["tag"])] = profile
            document_frequency.update(profile.keys())
        intent_count = max(1, len(profiles))
        idf = {
            term: math.log((intent_count + 1.0) / (frequency + 0.5)) + 1.0
            for term, frequency in document_frequency.items()
        }
        return profiles, idf

    def intent_profile_match(self, text: str) -> Optional[dict]:
        query_terms = set(retrieval_terms(text))
        known = {term for term in query_terms if term in self.intent_idf}
        if not known:
            return None
        total_weight = sum(self.intent_idf[term] for term in known) or 1.0
        query_concepts = {term for term in known if term.startswith("concept_")}
        ranked: List[Tuple[float, str, List[str]]] = []
        for tag, profile in self.intent_profiles.items():
            common = known & set(profile)
            if not common:
                continue
            weighted = sum(
                self.intent_idf[term] * (1.0 + 0.07 * min(4, profile.get(term, 1) - 1))
                for term in common
            )
            coverage = min(1.0, weighted / total_weight)
            distinct = len(common) / max(1, len(known))
            common_concepts = query_concepts & common
            concept_coverage = len(common_concepts) / max(1, len(query_concepts)) if query_concepts else 0.0
            score = 0.66 * coverage + 0.18 * distinct + 0.16 * concept_coverage
            if len(common) == 1 and not common_concepts:
                score *= 0.68
            ranked.append((min(1.0, score), tag, sorted(common)))
        if not ranked:
            return None
        ranked.sort(reverse=True)
        best_score, best_tag, matched = ranked[0]
        second_score = ranked[1][0] if len(ranked) > 1 else 0.0
        margin = best_score - second_score
        if margin >= 0.12:
            best_score = min(1.0, best_score + 0.05)
        return {
            "tag": best_tag,
            "score": best_score,
            "margin": margin,
            "matched": matched,
            "runner_up": ranked[1][1] if len(ranked) > 1 else None
        }

    def pattern_match(self, text: str) -> Optional[dict]:
        normalized = normalize_text(text)
        if not normalized:
            return None
        query_tokens = set(retrieval_terms(text))
        query_chars = {
            normalized[position:position + 3]
            for position in range(max(0, len(normalized) - 2))
            if " " not in normalized[position:position + 3]
        }
        best: Optional[dict] = None
        for tag, pattern, pattern_tokens, pattern_chars in self.pattern_index:
            if normalized == pattern:
                return {"tag": tag, "score": 1.0, "pattern": pattern}
            token_overlap = len(query_tokens & pattern_tokens)
            token_union = len(query_tokens | pattern_tokens) or 1
            query_coverage = token_overlap / max(1, len(query_tokens))
            pattern_coverage = token_overlap / max(1, len(pattern_tokens))
            jaccard = token_overlap / token_union
            char_overlap = len(query_chars & pattern_chars)
            char_union = len(query_chars | pattern_chars) or 1
            char_jaccard = char_overlap / char_union
            sequence = difflib.SequenceMatcher(None, normalized, pattern).ratio()
            substring = 0.10 if normalized in pattern or pattern in normalized else 0.0
            score = (
                0.27 * query_coverage
                + 0.17 * pattern_coverage
                + 0.16 * jaccard
                + 0.18 * char_jaccard
                + 0.22 * sequence
                + substring
            )
            candidate = {"tag": tag, "score": min(1.0, score), "pattern": pattern}
            if best is None or candidate["score"] > best["score"]:
                best = candidate
        return best

    def keyword_match(self, text: str) -> Optional[dict]:
        normalized = " " + normalize_text(text) + " "
        best: Optional[dict] = None
        for tag, hints in INTENT_HINTS.items():
            score = 0.0
            matched: List[str] = []
            for phrase, weight in hints.items():
                needle = normalize_text(phrase)
                if needle and needle in normalized:
                    score = max(score, float(weight))
                    matched.append(phrase.strip())
            if matched:
                score = min(1.0, score + 0.025 * max(0, len(matched) - 1))
                candidate = {"tag": tag, "score": score, "matched": matched}
                if best is None or candidate["score"] > best["score"]:
                    best = candidate
        return best

    @property
    def assistant_name(self) -> str:
        return self.dataset.get("assistant_name", APP_NAME)

    def close(self) -> None:
        self.store.close()

    def t(self, english: str, greek: str, language: Optional[str] = None) -> str:
        selected = language or self.last_language
        return greek if selected == "el" else english

    def resolve_language(self, text: str) -> str:
        detected = detect_language(text)
        if detected == "unsupported":
            return "unsupported"
        if self.language_mode in SUPPORTED_LANGUAGES:
            return self.language_mode
        if detected in SUPPORTED_LANGUAGES:
            self.last_language = detected
            try:
                self.store.set_setting("last_language", detected)
            except sqlite3.Error:
                pass
            return detected
        if detected == "neutral":
            return self.last_language
        return "unsupported"

    def set_language_mode(self, mode: str) -> None:
        mode = mode.casefold().strip()
        aliases = {
            "english": "en", "αγγλικα": "en", "αγγλικά": "en",
            "greek": "el", "ελληνικα": "el", "ελληνικά": "el",
            "automatic": "auto", "αυτοματα": "auto", "αυτόματα": "auto"
        }
        mode = aliases.get(mode, mode)
        if mode not in {"auto", "en", "el"}:
            raise ValueError("language mode must be auto, en, or el")
        self.language_mode = mode
        self.store.set_setting("language_mode", mode)
        if mode in SUPPORTED_LANGUAGES:
            self.last_language = mode
            self.store.set_setting("last_language", mode)

    def contextualize_query(self, text: str, language: str) -> Tuple[str, bool]:
        if not self.last_user_query or not is_followup_message(text, language):
            return text, False
        previous = self.last_user_query.strip()
        if not previous or normalize_text(previous) == normalize_text(text):
            return text, False
        return previous + " " + text, True

    def format_response(self, text: str, language: Optional[str] = None) -> str:
        language = language or self.last_language
        now = _dt.datetime.now().astimezone()
        name = self.store.get_memory("name") or self.store.get_memory("user_name") or ""
        if language == "el":
            date_text = f"{GREEK_WEEKDAYS[now.weekday()]}, {now.day} {GREEK_MONTHS[now.month - 1]} {now.year}"
        else:
            date_text = now.strftime("%A, %d %B %Y")
        replacements = {
            "{name}": name,
            "{name_suffix}": f", {name}" if name else "",
            "{time}": now.strftime("%H:%M:%S"),
            "{date}": date_text,
            "{data_dir}": str(self.data_dir),
            "{profile}": self.profile_name,
            "{model_size}": human_size(self.model_path.stat().st_size) if self.model_path.exists() else self.t("unknown", "άγνωστο", language)
        }
        for key, value in replacements.items():
            text = text.replace(key, value)
        return text

    def choose_intent_response(self, intent: dict, language: str) -> str:
        options = localized_intent_responses(intent, language)
        fresh = [option for option in options if option not in self.recent_responses]
        response = self.rng.choice(fresh or options)
        self.recent_responses.append(response)
        return self.format_response(response, language)
    def direct_utility_response(self, text: str, language: str) -> Optional[Tuple[str, str]]:
        stripped = text.strip()
        lowered = normalize_text(stripped)

        expression: Optional[str] = None
        if stripped.startswith("="):
            expression = stripped[1:].strip()
        elif lowered.startswith("calc "):
            expression = stripped[5:].strip()
        elif lowered.startswith("calculate "):
            expression = stripped[10:].strip()
        elif lowered.startswith("υπολογισε "):
            expression = stripped.split(maxsplit=1)[1].strip() if " " in stripped else ""
        if expression is not None:
            try:
                value = self.calculator.evaluate(expression)
                rendered = str(int(value)) if value.is_integer() else f"{value:.12g}"
                return self.t(f"Result: {rendered}", f"Αποτέλεσμα: {rendered}", language), "calculator"
            except (ValueError, ZeroDivisionError, OverflowError, SyntaxError) as error:
                return self.t(f"Calculation error: {error}", f"Σφάλμα υπολογισμού: {error}", language), "calculator_error"

        conversion = re.match(
            r"^(?:convert|conversion|μετατρεψε|μετετρεψε|μετατροπη)\s+(-?\d+(?:[.,]\d+)?)\s*([^\s]+)\s+(?:to|into|σε)\s+([^\s?]+)",
            lowered
        )
        if conversion:
            try:
                value = float(conversion.group(1).replace(",", "."))
                source, target = conversion.group(2), conversion.group(3)
                converted = convert_units(value, source, target)
                rendered = f"{converted:.12g}"
                return self.t(
                    f"{value:g} {source} = {rendered} {target}",
                    f"{value:g} {source} = {rendered} {target}",
                    language
                ), "unit_conversion"
            except ValueError as error:
                return self.t(f"Conversion error: {error}", f"Σφάλμα μετατροπής: {error}", language), "unit_conversion_error"

        if lowered in {"what time is it", "tell me the time", "current time", "τι ωρα ειναι", "πες μου την ωρα"}:
            return self.format_response(self.t("The local time is {time}.", "Η τοπική ώρα είναι {time}.", language), language), "time"
        if lowered in {"what date is it", "what is the date", "today's date", "current date", "τι ημερομηνια εχουμε", "τι μερα ειναι"}:
            return self.format_response(self.t("The local date is {date}.", "Η τοπική ημερομηνία είναι {date}.", language), language), "date"

        if lowered in {normalize_text(value) for value in ("what is my name", "what's my name", "do you know my name", "πως με λένε", "ποιο είναι το όνομά μου", "θυμάσαι το όνομά μου")}:
            name = self.store.get_memory("name") or self.store.get_memory("user_name")
            if name:
                return self.t(f"Your name is {name}.", f"Σε λένε {name}.", language), "name_recall"
            return self.t("You have not told me your name yet.", "Δεν μου έχεις πει ακόμη το όνομά σου.", language), "name_recall_missing"

        name_match = re.match(
            r"^(?:my name is|call me|i am called|με λένε|με λενε|το όνομά μου είναι|το ονομα μου ειναι)\s+(.+?)[.!]?$",
            stripped, flags=re.IGNORECASE
        )
        if name_match:
            name = name_match.group(1).strip()[:80]
            self.store.set_memory("name", name)
            return self.t(f"I will remember your name as {name}.", f"Θα θυμάμαι ότι σε λένε {name}.", language), "name_memory"

        remember_match = re.match(
            r"^(?:remember(?: that)?|θυμήσου(?: ότι)?|θυμησου(?: οτι)?)\s+(.+?)\s+(?:is|είναι|ειναι)\s+(.+)$",
            stripped, flags=re.IGNORECASE
        )
        if remember_match:
            key, value = remember_match.groups()
            self.store.set_memory(key, value)
            return self.t(
                f"Remembered: {key.strip()} = {value.strip()}",
                f"Το θυμήθηκα: {key.strip()} = {value.strip()}",
                language
            ), "memory_write"

        recall_match = re.match(
            r"^(?:what is|what's|do you remember|τι είναι|τι ειναι|θυμάσαι|θυμασαι)\s+(?:my\s+|το\s+)?(.+?)[?]?$",
            stripped, flags=re.IGNORECASE
        )
        if recall_match:
            key = recall_match.group(1).strip()
            for candidate in (key, "my " + key, key.replace("my ", "", 1)):
                value = self.store.get_memory(candidate)
                if value is not None:
                    return f"{candidate}: {value}", "memory_read"

        summary_prefixes = ("summarize:", "summary:", "συνοψη:", "περιληψη:", "σύνοψη:", "περίληψη:")
        for prefix in summary_prefixes:
            if stripped.casefold().startswith(prefix.casefold()):
                body = stripped[len(prefix):].strip()
                if len(body) < 40:
                    return self.t("Provide a longer text after the colon.", "Δώσε μεγαλύτερο κείμενο μετά την άνω και κάτω τελεία.", language), "summary_error"
                if detect_language(body) == "unsupported":
                    return self.t("Only English and Greek text is supported.", "Υποστηρίζεται μόνο αγγλικό και ελληνικό κείμενο.", language), "language_reject"
                return extractive_summary(body, language), "summary"

        if lowered in {"system info", "device info", "phone status", "memory status", "πληροφοριες συστηματος", "κατασταση κινητου"}:
            return self.system_report(language), "system"
        return None

    def system_report(self, language: Optional[str] = None) -> str:
        language = language or self.last_language
        available = available_memory_bytes()
        total = total_memory_bytes()
        try:
            usage = shutil.disk_usage(self.data_dir)
            disk_en = f"{human_size(usage.free)} free of {human_size(usage.total)}"
            disk_el = f"{human_size(usage.free)} ελεύθερα από {human_size(usage.total)}"
        except OSError:
            disk_en = "unavailable"
            disk_el = "μη διαθέσιμο"
        return self.t(
            f"Python {sys.version.split()[0]}; platform {sys.platform}; RAM {human_size(available)} available of {human_size(total)}; storage {disk_en}; profile {self.profile_name}; language mode {self.language_mode}.",
            f"Python {sys.version.split()[0]}; πλατφόρμα {sys.platform}; διαθέσιμη RAM {human_size(available)} από {human_size(total)}; αποθήκευση {disk_el}; profile {self.profile_name}; λειτουργία γλώσσας {self.language_mode}.",
            language
        )

    def neural_response(self, text: str, language: str) -> Tuple[str, dict]:
        neural_tag, neural_confidence, coverage, top = self.model.predict(text)
        pattern = self.pattern_match(text)
        keyword = self.keyword_match(text)
        semantic = self.intent_profile_match(text)
        chosen_tag = neural_tag
        combined_confidence = neural_confidence
        route = "neural"

        if pattern is not None:
            pattern_tag = str(pattern["tag"])
            pattern_score = float(pattern["score"])
            if pattern_tag == neural_tag:
                combined_confidence = max(
                    neural_confidence,
                    0.62 * neural_confidence + 0.38 * pattern_score,
                    0.86 * pattern_score
                )
                route = "hybrid"
            elif pattern_score >= 0.83:
                chosen_tag = pattern_tag
                combined_confidence = pattern_score
                route = "pattern"
            elif pattern_score >= 0.69 and neural_confidence < 0.46:
                chosen_tag = pattern_tag
                combined_confidence = pattern_score * 0.94
                route = "pattern"

        if keyword is not None:
            keyword_tag = str(keyword["tag"])
            keyword_score = float(keyword["score"])
            if keyword_score >= 0.74:
                if pattern is not None and float(pattern.get("score", 0.0)) >= 0.97 and keyword_tag != pattern.get("tag"):
                    pass
                elif keyword_tag == neural_tag:
                    combined_confidence = max(combined_confidence, keyword_score, 0.58 * neural_confidence + 0.42 * keyword_score)
                    chosen_tag = keyword_tag
                    route = "hybrid_keyword"
                elif pattern is not None and keyword_tag == pattern.get("tag"):
                    combined_confidence = max(keyword_score, float(pattern["score"]))
                    chosen_tag = keyword_tag
                    route = "keyword_pattern"
                elif pattern is not None and float(pattern.get("score", 0.0)) >= 0.97:
                    pass
                elif keyword_score >= 0.84 or neural_confidence < 0.52:
                    chosen_tag = keyword_tag
                    combined_confidence = keyword_score
                    route = "keyword"

        if semantic is not None:
            semantic_tag = str(semantic["tag"])
            semantic_score = float(semantic["score"])
            exact_pattern = pattern is not None and float(pattern.get("score", 0.0)) >= 0.97
            strong_keyword = keyword is not None and float(keyword.get("score", 0.0)) >= 0.90
            keyword_conflict = strong_keyword and str(keyword.get("tag")) != semantic_tag
            if not exact_pattern and not keyword_conflict:
                if semantic_tag == chosen_tag:
                    combined_confidence = max(
                        combined_confidence,
                        0.56 * combined_confidence + 0.44 * semantic_score,
                        semantic_score
                    )
                    route = route + "_semantic"
                elif semantic_score >= 0.68 and float(semantic.get("margin", 0.0)) >= 0.07:
                    chosen_tag = semantic_tag
                    combined_confidence = semantic_score
                    route = "semantic"
                elif combined_confidence < 0.47 and semantic_score >= 0.52:
                    chosen_tag = semantic_tag
                    combined_confidence = semantic_score
                    route = "semantic"

        adjusted_threshold = self.confidence_threshold
        if len(word_tokens(text)) <= 1:
            adjusted_threshold += 0.04
        if coverage < 0.40:
            adjusted_threshold += 0.05
        if route in {"pattern", "keyword", "keyword_pattern", "hybrid_keyword", "semantic"} or "semantic" in route:
            adjusted_threshold = min(adjusted_threshold, 0.56)

        intent = self.intent_lookup.get(chosen_tag)
        if intent and combined_confidence >= adjusted_threshold:
            response = self.choose_intent_response(intent, language)
            return response, {
                "route": route,
                "intent": chosen_tag,
                "confidence": combined_confidence,
                "neural_intent": neural_tag,
                "neural_confidence": neural_confidence,
                "coverage": coverage,
                "pattern": pattern,
                "keyword": keyword,
                "semantic": semantic,
                "top": top,
                "threshold": adjusted_threshold
            }

        fallback = self.rng.choice(FALLBACK_RESPONSES[language])
        return self.format_response(fallback, language), {
            "route": "fallback",
            "intent": chosen_tag,
            "confidence": combined_confidence,
            "neural_intent": neural_tag,
            "neural_confidence": neural_confidence,
            "coverage": coverage,
            "pattern": pattern,
            "keyword": keyword,
            "semantic": semantic,
            "top": top,
            "threshold": adjusted_threshold
        }

    def answer(self, text: str) -> Tuple[str, dict]:
        original_text = text.strip()[:MAX_INPUT_CHARS]
        language = self.resolve_language(original_text)
        if language == "unsupported":
            response = "I can communicate only in English and Greek. / Μπορώ να επικοινωνώ μόνο στα Αγγλικά και στα Ελληνικά."
            details = {"route": "language_reject", "language": "unsupported"}
            return response, details

        contextual_text, context_used = self.contextualize_query(original_text, language)
        specialist = self.specialists.select(contextual_text)
        utility = self.direct_utility_response(original_text, language)
        if utility is not None:
            response, route = utility
            details = {"route": route, "language": language, "context_used": False}
        else:
            candidates = self.store.retrieve_many(contextual_text, limit=6, language=language)
            response = ""
            details: dict = {"language": language, "context_used": context_used}

            qa_candidates = [candidate for candidate in candidates if candidate["kind"] == "qa"]
            best_qa = qa_candidates[0] if qa_candidates else None
            if best_qa and best_qa["overlap"] >= 1 and best_qa["score"] >= 0.43:
                response = str(best_qa["response"])
                details = {"route": "retrieval_qa", **details, **best_qa}
            else:
                document_candidates = [candidate for candidate in candidates if candidate["kind"] == "document"]
                best_document = document_candidates[0] if document_candidates else None
                if best_document and best_document["overlap"] >= 1 and best_document["score"] >= 0.37:
                    extracted = extractive_document_answer(contextual_text, document_candidates, language)
                    response = extracted or str(best_document["response"])
                    sources = []
                    for candidate in document_candidates[:3]:
                        source = str(candidate.get("source", ""))
                        if source and source not in sources:
                            sources.append(source)
                    if sources:
                        label = self.t("Local source", "Τοπική πηγή", language)
                        response += "\n[" + label + ": " + "; ".join(sources[:2]) + "]"
                    details = {"route": "retrieval_document", **details, "candidates": document_candidates[:3]}

            if not response:
                specialist_knowledge = self.specialists.knowledge_answer(
                    contextual_text, language, selected=specialist
                )
                if specialist_knowledge is not None:
                    response = str(specialist_knowledge["response"])
                    details = {
                        **details,
                        "route": "specialist_model",
                        "specialist": specialist_knowledge["specialist"],
                        "specialist_match": specialist_knowledge["match_score"],
                        "specialist_pattern": specialist_knowledge["pattern"],
                    }

            if not response:
                response, neural_details = self.neural_response(contextual_text, language)
                details = {**details, **neural_details}
                should_use_llm = (
                    self.llm_mode == "always"
                    or (self.llm_mode == "fallback" and neural_details.get("route") == "fallback")
                    or (
                        self.llm_mode != "off"
                        and specialist is not None
                        and float(specialist.get("score", 0.0)) >= 4.0
                    )
                )
                if should_use_llm and self.local_llm.available:
                    try:
                        response, llm_details = self.ask_local_llm(
                            contextual_text, language, candidates, specialist=specialist
                        )
                        details = {**details, **llm_details, "neural_fallback": neural_details}
                    except RuntimeError as error:
                        details["llm_error"] = str(error)
                if specialist is not None:
                    details["specialist_candidate"] = specialist
                if candidates:
                    details["retrieval_candidates"] = [
                        {
                            "score": candidate["score"],
                            "kind": candidate["kind"],
                            "source": candidate["source"],
                            "language": candidate.get("language")
                        }
                        for candidate in candidates[:3]
                    ]

        self.session_history.append(("user", original_text))
        self.session_history.append(("assistant", response))
        self.last_user_query = original_text
        self.last_details = details
        try:
            self.store.add_history("user", original_text)
            self.store.add_history("assistant", response)
        except sqlite3.Error:
            pass
        return response, details

    def retrain(self, epochs_override: Optional[int] = None) -> None:
        model, dataset, metadata = train_classifier(
            self.dataset_path,
            self.model_path,
            self.metadata_path,
            self.profile_name,
            epochs_override=epochs_override,
            verbose=True
        )
        self.model = model
        self.dataset = dataset
        self.metadata = metadata
        self.intent_lookup = {item["tag"]: item for item in dataset["intents"]}
        self.pattern_index = self._build_pattern_index(dataset)
        self.intent_profiles, self.intent_idf = self._build_intent_profiles(dataset)

    def build_language_model(self, extra_path: Optional[Path] = None) -> dict:
        model = NGramLanguageModel(order=3)
        texts: List[str] = []
        for intent in self.dataset["intents"]:
            texts.extend(intent["patterns"])
            texts.extend(intent["responses"])
        rows = self.store.connection.execute(
            "SELECT prompt,response FROM items ORDER BY id DESC LIMIT 12000"
        ).fetchall()
        for row in rows:
            texts.append(str(row["prompt"]))
            texts.append(str(row["response"]))
        if extra_path is not None:
            extra_path = extra_path.expanduser().resolve()
            for file_path in iter_ingest_files(extra_path):
                try:
                    if 0 < file_path.stat().st_size <= MAX_FILE_BYTES:
                        texts.append(clean_document_text(
                            decode_text_bytes(file_path.read_bytes()), file_path.suffix.casefold()
                        ))
                except OSError:
                    continue
        texts = [text for text in texts if detect_language(text) in {"en", "el", "neutral"}]
        sentence_count = model.train_texts(texts)
        model.save(self.language_model_path)
        self.language_model = model
        return {
            "sentences": sentence_count,
            "contexts": len(model.transitions),
            "file": str(self.language_model_path),
            "size": self.language_model_path.stat().st_size
        }

    def set_llm_mode(self, mode: str) -> None:
        aliases = {"on": "fallback", "auto": "fallback", "yes": "fallback", "no": "off"}
        mode = aliases.get(mode.casefold().strip(), mode.casefold().strip())
        if mode not in {"off", "fallback", "always"}:
            raise ValueError("LLM mode must be off, fallback, or always.")
        self.llm_mode = mode
        self.store.set_setting("llm_mode", mode)

    def set_llm_model(self, name: str) -> str:
        selected = self.local_llm.set_model(name)
        self.store.set_setting("llm_model", selected)
        return selected

    def set_llm_cpu_profile(self, name: str) -> str:
        selected = self.local_llm.set_cpu_profile(name)
        self.store.set_setting("llm_cpu_profile", selected)
        return selected

    def llm_context(self, candidates: Sequence[dict]) -> str:
        pieces: List[str] = []
        for candidate in candidates[:4]:
            response = str(candidate.get("response", "")).strip()
            source = str(candidate.get("source", "")).strip()
            if response:
                pieces.append((f"Source: {source}\n" if source else "") + response[:1100])
        memories = self.store.list_memories(12)
        if memories:
            pieces.append("Saved user facts:\n" + "\n".join(f"{key} = {value}" for key, value in memories))
        return "\n\n".join(pieces)[:5000]

    def ask_local_llm(
        self,
        text: str,
        language: str,
        candidates: Sequence[dict] = (),
        specialist: Optional[dict] = None,
    ) -> Tuple[str, dict]:
        context = self.llm_context(candidates)
        specialist_instruction = self.specialists.instruction(specialist, language)
        response = self.local_llm.generate(
            text,
            language,
            context=context,
            specialist_instruction=specialist_instruction,
        )
        return response, {
            "route": "local_gguf_llm",
            "language": language,
            "llm_mode": self.llm_mode,
            "model": str(self.local_llm.model_path or "missing"),
            "model_profile": self.local_llm.active_model,
            "context_chars": len(context),
            "specialist": specialist.get("id") if specialist else None,
        }

    def stats_text(self) -> str:
        counts = self.store.counts()
        lines = [
            "Model statistics",
            f"  Profile:             {self.profile_name}",
            f"  Parameters:          {self.model.parameter_count():,}",
            f"  Hashed input size:   {self.model.hash_size:,}",
            f"  Hidden layers:       {self.model.hidden1_size} -> {self.model.hidden2_size}",
            f"  Intents:             {len(self.model.tags)}",
            f"  Training examples:   {self.metadata.get('example_count', '?')}",
            f"  Training accuracy:   {float(self.metadata.get('train_accuracy', 0)) * 100:.1f}%",
            f"  Validation accuracy: {float(self.metadata.get('validation_accuracy', 0)) * 100:.1f}%",
            f"  Training time:       {float(self.metadata.get('training_seconds', 0)):.2f}s",
            f"  Model disk size:     {human_size(self.model_path.stat().st_size) if self.model_path.exists() else 'missing'}",
            f"  Taught Q&A pairs:    {counts['qa']}",
            f"  Document chunks:     {counts['document']}",
            f"  Indexed terms:       {counts['terms']:,}",
            f"  Persistent memories: {counts['memories']}",
            f"  History entries:     {counts['history']}",
            f"  Micro language model:{human_size(self.language_model_path.stat().st_size) if self.language_model_path.exists() else ' not installed'} ({self.micro_model_variant})",
            f"  GGUF LLM mode:       {self.llm_mode}",
            f"  Active GGUF model:   {self.local_llm.active_model}",
            f"  CPU runtime profile: {self.local_llm.requested_cpu_profile} -> {self.local_llm.runtime_settings()['resolved']}",
            f"  Active model size:   {human_size(self.local_llm.model_path.stat().st_size) if self.local_llm.model_path else 'not installed'}",
            f"  Bundled GGUF models: {len(self.local_llm.model_paths)}/{len(EXTERNAL_LLM_MODELS)} detected",
            f"  Specialist models:   {sum(1 for item in self.specialists.status() if item['loaded'])}/{len(self.specialists.FILES)} loaded",
            f"  llama.cpp:           {str(self.local_llm.binary_path) if self.local_llm.binary_path else 'not installed'}"
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Chat command handling
# ---------------------------------------------------------------------------


HELP_TEXT_EN = """
Core commands
  /help                         Show this command list
  /quit                         Exit safely
  /language auto|en|el          Automatic, English, or Greek output mode
  /stats                        Show neural and knowledge statistics
  /models                       Show every bundled model and active selection
  /where                        Show every important file path
  /system                       Show RAM, storage, Python, and profile
  /debug                        Toggle routing and confidence details
  /why                          Explain how the previous answer was selected

Learning and knowledge
  /teach QUESTION | ANSWER      Add an immediately searchable Q&A pair
  /correct ANSWER               Replace the answer to your previous question
  /ingest PATH                  Index English/Greek text files or a directory
  /dork QUERY                   Safely search public web pages and learn them
  /web-learn QUERY              Alias of /dork; supports safe search operators
  /summarize PATH               Create an extractive summary of a text file
  /remember KEY = VALUE         Store a persistent local memory
  /memories                     List saved memories
  /forget KEY                   Delete one persistent memory
  /train                        Retrain the neural intent model
  /build-lm [PATH]              Build the experimental local generator
  /generate [PROMPT]            Generate with the bundled bilingual MicroLM
  /llm off|fallback|always      Control the local GGUF fallback
  /llm-model fast|quality       Select low-RAM or higher-quality model
  /cpu-profile auto|ultra_eco|eco|entry|balanced|performance
                                Override automatic hardware tuning
  /ask-llm PROMPT               Ask the selected GGUF model directly
  /llm-status                   Check GGUF models, checksums, and llama.cpp

Maintenance
  /history                      Show recent local conversation history
  /clear-history                Delete saved conversation history
  /export                       Export knowledge and memories to JSON
  /backup                       Create a compressed backup archive
  /benchmark                    Measure prediction and retrieval speed
  /profile                      Explain available model profiles

Direct tools
  = (12 + 8) * 3
  calc sqrt(144) + sin(pi / 2)
  convert 5 km to miles
  summarize: paste a long English or Greek text here
""".strip()

HELP_TEXT_EL = """
Βασικές εντολές
  /βοήθεια                      Εμφάνιση όλων των εντολών
  /έξοδος                       Ασφαλής έξοδος
  /γλώσσα auto|en|el            Αυτόματη, αγγλική ή ελληνική λειτουργία
  /stats                        Στατιστικά μοντέλου και γνώσης
  /μοντέλα                      Όλα τα μοντέλα και η ενεργή επιλογή
  /where                        Διαδρομές σημαντικών αρχείων
  /system                       RAM, αποθήκευση, Python και profile
  /debug                        Λεπτομέρειες δρομολόγησης και βεβαιότητας
  /why                          Εξήγηση επιλογής της προηγούμενης απάντησης

Μάθηση και γνώση
  /teach ΕΡΩΤΗΣΗ | ΑΠΑΝΤΗΣΗ     Άμεση προσθήκη γνώσης
  /διόρθωση ΑΠΑΝΤΗΣΗ            Διόρθωση της προηγούμενης απάντησης
  /ingest ΔΙΑΔΡΟΜΗ              Ευρετηρίαση αγγλικών/ελληνικών αρχείων
  /dork ΕΡΩΤΗΜΑ                  Ασφαλής έρευνα δημόσιου ιστού και μάθηση
  /web-learn ΕΡΩΤΗΜΑ             Ίδια λειτουργία με /dork
  /σύνοψη ΔΙΑΔΡΟΜΗ              Εξαγωγική σύνοψη αρχείου κειμένου
  /remember ΚΛΕΙΔΙ = ΤΙΜΗ       Αποθήκευση μόνιμης μνήμης
  /memories                     Προβολή αποθηκευμένων μνημών
  /forget ΚΛΕΙΔΙ                Διαγραφή μνήμης
  /train                        Επανεκπαίδευση νευρωνικού μοντέλου
  /build-lm [ΔΙΑΔΡΟΜΗ]          Δημιουργία πειραματικού generator
  /generate [PROMPT]            Παραγωγή με το ενσωματωμένο MicroLM
  /llm off|fallback|always      Έλεγχος του τοπικού GGUF fallback
  /μοντέλο fast|quality        Επιλογή χαμηλής RAM ή καλύτερης ποιότητας
  /επεξεργαστής auto|ultra_eco|eco|entry|balanced|performance
                                Παράκαμψη αυτόματης ρύθμισης hardware
  /ask-llm PROMPT               Άμεση ερώτηση στο επιλεγμένο GGUF μοντέλο
  /llm-status                   Έλεγχος GGUF μοντέλων, checksums και llama.cpp

Συντήρηση
  /history                      Πρόσφατο τοπικό ιστορικό
  /clear-history                Διαγραφή ιστορικού
  /export                       Εξαγωγή γνώσης και μνημών
  /backup                       Δημιουργία συμπιεσμένου backup
  /benchmark                    Μέτρηση ταχύτητας
  /profile                      Επεξήγηση profiles

Άμεσα εργαλεία
  = (12 + 8) * 3
  calc sqrt(144) + sin(pi / 2)
  μετέτρεψε 5 km σε miles
  σύνοψη: επικόλλησε εδώ μεγάλο ελληνικό ή αγγλικό κείμενο
""".strip()


def parse_teach_argument(argument: str) -> Optional[Tuple[str, str]]:
    if "|" not in argument:
        return None
    question, answer = argument.split("|", 1)
    question = question.strip()
    answer = answer.strip()
    return (question, answer) if question and answer else None


def create_backup(data_dir: Path) -> Path:
    backup_dir = data_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = backup_dir / f"PocketAI_Bilingual_MAX_{stamp}.tar.gz"
    temporary = archive_path.with_suffix(archive_path.suffix + ".tmp")
    with tarfile.open(temporary, "w:gz", compresslevel=6) as archive:
        for child in sorted(data_dir.iterdir()):
            if child.resolve() == backup_dir.resolve():
                continue
            archive.add(child, arcname=child.name, recursive=True)
    temporary.replace(archive_path)
    return archive_path


def benchmark_assistant(assistant: PocketAssistant, iterations: int = 1200) -> dict:
    samples = [
        "hello there", "how do I train the neural network", "what can you do offline",
        "help me protect my password", "how do I index a document", "tell me about termux",
        "τι μπορείς να κάνεις", "χρειάζεσαι ίντερνετ", "what is machine learning"
    ]
    started = time.perf_counter()
    for index in range(iterations):
        assistant.model.predict(samples[index % len(samples)])
    neural_seconds = time.perf_counter() - started

    started = time.perf_counter()
    for index in range(min(300, iterations)):
        assistant.store.retrieve(samples[index % len(samples)])
    retrieval_seconds = time.perf_counter() - started
    return {
        "neural_iterations": iterations,
        "neural_seconds": neural_seconds,
        "neural_per_second": iterations / max(neural_seconds, 1e-12),
        "retrieval_iterations": min(300, iterations),
        "retrieval_seconds": retrieval_seconds,
        "retrieval_per_second": min(300, iterations) / max(retrieval_seconds, 1e-12)
    }


def handle_command(assistant: PocketAssistant, command_line: str) -> Tuple[bool, Optional[str]]:
    command_line = command_line.strip()
    raw_command, _, argument = command_line.partition(" ")
    normalized_command = normalize_text(raw_command)
    aliases = {
        "/βοηθεια": "/help", "/βοήθεια": "/help",
        "/έρευνα": "/dork", "/ερευνα": "/dork", "/ιστομαθηση": "/web-learn",
        "/μοντέλο": "/llm-model", "/μοντελο": "/llm-model",
        "/μοντέλα": "/models", "/μοντελα": "/models",
        "/επεξεργαστησ": "/cpu-profile", "/επεξεργαστής": "/cpu-profile", "/cpu": "/cpu-profile",
        "/λειτουργια-llm": "/llm", "/λειτουργία-llm": "/llm",
        "/εξοδοσ": "/quit", "/έξοδοσ": "/quit", "/εξοδος": "/quit",
        "/γλωσσα": "/language", "/γλώσσα": "/language",
        "/μαθε": "/teach", "/μάθε": "/teach",
        "/διορθωση": "/correct", "/διόρθωση": "/correct",
        "/συνοψη": "/summarize", "/σύνοψη": "/summarize",
        "/θυμησου": "/remember", "/θυμήσου": "/remember",
        "/μνημεσ": "/memories", "/μνήμεσ": "/memories", "/μνημες": "/memories",
        "/ξεχασε": "/forget", "/ξέχασε": "/forget",
        "/εκπαιδευση": "/train", "/εκπαίδευση": "/train",
        "/ιστορικο": "/history", "/ιστορικό": "/history",
        "/γιατι": "/why", "/γιατί": "/why"
    }
    command = aliases.get(normalized_command, raw_command.casefold())
    language = "el" if GREEK_CHAR_RE.search(raw_command) else assistant.last_language
    if assistant.language_mode in SUPPORTED_LANGUAGES:
        language = assistant.language_mode
    argument = argument.strip()

    if command in {"/quit", "/exit"}:
        return False, assistant.t(f"{assistant.assistant_name}: Goodbye.", f"{assistant.assistant_name}: Αντίο.", language)
    if command == "/help":
        return True, HELP_TEXT_EL if language == "el" else HELP_TEXT_EN
    if command == "/language":
        if not argument:
            return True, assistant.t(
                f"Current language mode: {assistant.language_mode}. Use /language auto, /language en, or /language el.",
                f"Τρέχουσα λειτουργία γλώσσας: {assistant.language_mode}. Χρησιμοποίησε /γλώσσα auto, en ή el.",
                language
            )
        try:
            assistant.set_language_mode(argument)
            display = LANGUAGE_NAMES.get(assistant.language_mode, assistant.language_mode)
            return True, assistant.t(f"Language mode set to {display}.", f"Η λειτουργία γλώσσας ορίστηκε σε {display}.", assistant.last_language)
        except ValueError as error:
            return True, assistant.t(str(error), "Η γλώσσα πρέπει να είναι auto, en ή el.", language)
    if command == "/stats":
        return True, assistant.stats_text()
    if command == "/models":
        models_dir = Path(__file__).resolve().parent / "Models"
        manifest_path = Path(__file__).resolve().parent / "Other Files" / "Documentation" / "MODEL_MANIFEST.json"
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            entries = payload.get("models", []) if isinstance(payload, dict) else []
        except (OSError, ValueError, json.JSONDecodeError):
            entries = []
        selected_classifier = assistant.profile_name
        selected_gguf = assistant.local_llm.active_model
        lines_en = [
            "Bundled AI model catalog",
            f"Active neural classifier: {selected_classifier}",
            f"Active GGUF model: {selected_gguf}",
            f"MicroLM variant: {assistant.micro_model_variant}",
            "",
        ]
        lines_el = [
            "Κατάλογος ενσωματωμένων μοντέλων AI",
            f"Ενεργός νευρωνικός classifier: {selected_classifier}",
            f"Ενεργό GGUF μοντέλο: {selected_gguf}",
            f"Παραλλαγή MicroLM: {assistant.micro_model_variant}",
            "",
        ]
        if entries:
            for item in entries:
                file_path = Path(__file__).resolve().parent / str(item.get("file", ""))
                state = "ready" if file_path.is_file() else "missing"
                state_el = "έτοιμο" if file_path.is_file() else "λείπει"
                name = str(item.get("name", item.get("id", "model")))
                kind = str(item.get("kind", "model"))
                size = human_size(file_path.stat().st_size) if file_path.is_file() else "0 B"
                lines_en.append(f"- {name} | {kind} | {size} | {state}")
                lines_el.append(f"- {name} | {kind} | {size} | {state_el}")
        else:
            lines_en.append(f"Models folder: {models_dir}")
            lines_el.append(f"Φάκελος μοντέλων: {models_dir}")
        return True, "\n".join(lines_el if language == "el" else lines_en)
    if command == "/where":
        return True, "\n".join([
            assistant.t(f"Data directory:   {assistant.data_dir}", f"Φάκελος δεδομένων: {assistant.data_dir}", language),
            assistant.t(f"Dataset:          {assistant.dataset_path}", f"Dataset:            {assistant.dataset_path}", language),
            assistant.t(f"Neural model:     {assistant.model_path}", f"Νευρωνικό μοντέλο: {assistant.model_path}", language),
            assistant.t(f"Model metadata:   {assistant.metadata_path}", f"Metadata μοντέλου:  {assistant.metadata_path}", language),
            assistant.t(f"Knowledge DB:     {assistant.database_path}", f"Βάση γνώσης:       {assistant.database_path}", language),
            assistant.t(f"Micro model:      {assistant.language_model_path}", f"Micro μοντέλο:      {assistant.language_model_path}", language),
            assistant.t(f"Bundled models:   {Path(__file__).resolve().parent / 'Models'}", f"Ενσωματωμένα μοντέλα: {Path(__file__).resolve().parent / 'Models'}", language),
            assistant.t(f"Classifier source:{Path(__file__).resolve().parent / 'Models' / ('pretrained_' + assistant.profile_name)}", f"Πηγή classifier:    {Path(__file__).resolve().parent / 'Models' / ('pretrained_' + assistant.profile_name)}", language),
            assistant.t(f"Specialists:      {Path(__file__).resolve().parent / 'Models'}", f"Specialists:        {Path(__file__).resolve().parent / 'Models'}", language),
            assistant.t(f"Fast GGUF model:  {Path(__file__).resolve().parent / 'Models' / EXTERNAL_LLM_MODELS['fast']['filename']}", f"Γρήγορο GGUF:       {Path(__file__).resolve().parent / 'Models' / EXTERNAL_LLM_MODELS['fast']['filename']}", language),
            assistant.t(f"Quality GGUF:     {Path(__file__).resolve().parent / 'Models' / EXTERNAL_LLM_MODELS['quality']['filename']}", f"Ποιοτικό GGUF:      {Path(__file__).resolve().parent / 'Models' / EXTERNAL_LLM_MODELS['quality']['filename']}", language),
            assistant.t(f"llama.cpp:        {assistant.data_dir / 'llama.cpp' / 'build' / 'bin' / 'llama-cli'}", f"llama.cpp:          {assistant.data_dir / 'llama.cpp' / 'build' / 'bin' / 'llama-cli'}", language)
        ])
    if command == "/system":
        return True, assistant.system_report(language)
    if command == "/debug":
        assistant.debug = not assistant.debug
        return True, assistant.t(
            f"Debug details {'enabled' if assistant.debug else 'disabled'}.",
            f"Οι λεπτομέρειες debug {'ενεργοποιήθηκαν' if assistant.debug else 'απενεργοποιήθηκαν'}.",
            language
        )
    if command == "/why":
        if not assistant.last_details:
            return True, assistant.t("There is no previous answer to explain.", "Δεν υπάρχει προηγούμενη απάντηση για εξήγηση.", language)
        route = assistant.last_details.get("route", "unknown")
        confidence = assistant.last_details.get("confidence")
        intent = assistant.last_details.get("intent")
        parts = [assistant.t(f"Route: {route}", f"Διαδρομή: {route}", language)]
        if intent:
            parts.append(assistant.t(f"Intent: {intent}", f"Πρόθεση: {intent}", language))
        if isinstance(confidence, (int, float)):
            parts.append(assistant.t(f"Confidence: {confidence:.3f}", f"Βεβαιότητα: {confidence:.3f}", language))
        if assistant.last_details.get("context_used"):
            parts.append(assistant.t("The previous user message was used as context.", "Χρησιμοποιήθηκε το προηγούμενο μήνυμα ως συμφραζόμενο.", language))
        return True, "\n".join(parts)
    if command == "/teach":
        parsed = parse_teach_argument(argument)
        if parsed is None:
            try:
                question = input(assistant.t("Question/example: ", "Ερώτηση/παράδειγμα: ", language)).strip()
                answer = input(assistant.t("Desired answer: ", "Επιθυμητή απάντηση: ", language)).strip()
            except (EOFError, KeyboardInterrupt):
                return True, assistant.t("Teaching cancelled.", "Η διδασκαλία ακυρώθηκε.", language)
            if not question or not answer:
                return True, assistant.t("Teaching cancelled because a field was empty.", "Η διδασκαλία ακυρώθηκε επειδή υπήρχε κενό πεδίο.", language)
        else:
            question, answer = parsed
        if detect_language(question) == "unsupported" or detect_language(answer) == "unsupported":
            return True, assistant.t("Only English and Greek teaching data is accepted.", "Γίνονται δεκτά μόνο αγγλικά και ελληνικά δεδομένα διδασκαλίας.", language)
        item_id = assistant.store.teach(question, answer)
        return True, assistant.t(
            f"Learned Q&A item {item_id}. It is searchable immediately.",
            f"Αποθηκεύτηκε το στοιχείο γνώσης {item_id} και είναι άμεσα διαθέσιμο.",
            language
        )
    if command == "/correct":
        if not assistant.last_user_query:
            return True, assistant.t("There is no previous question to correct.", "Δεν υπάρχει προηγούμενη ερώτηση για διόρθωση.", language)
        if not argument:
            return True, assistant.t("Usage: /correct ANSWER", "Χρήση: /διόρθωση ΑΠΑΝΤΗΣΗ", language)
        if detect_language(argument) == "unsupported":
            return True, assistant.t("The correction must be English or Greek.", "Η διόρθωση πρέπει να είναι στα Αγγλικά ή στα Ελληνικά.", language)
        item_id = assistant.store.teach(assistant.last_user_query, argument)
        return True, assistant.t(
            f"Correction saved as Q&A item {item_id} for: {assistant.last_user_query}",
            f"Η διόρθωση αποθηκεύτηκε ως στοιχείο {item_id} για: {assistant.last_user_query}",
            language
        )
    if command == "/ingest":
        if not argument:
            return True, assistant.t("Usage: /ingest PATH", "Χρήση: /ingest ΔΙΑΔΡΟΜΗ", language)
        try:
            result = ingest_path(assistant.store, Path(argument))
            message = assistant.t(
                f"Indexed {result['files_indexed']} of {result['files_seen']} files, added {result['chunks_added']} chunks, read {human_size(result['bytes_read'])}.",
                f"Ευρετηριάστηκαν {result['files_indexed']} από {result['files_seen']} αρχεία, προστέθηκαν {result['chunks_added']} τμήματα και διαβάστηκαν {human_size(result['bytes_read'])}.",
                language
            )
            if result["skipped"]:
                message += assistant.t("\nSkipped examples:\n  ", "\nΠαραλείφθηκαν:\n  ", language) + "\n  ".join(result["skipped"][:8])
            return True, message
        except (OSError, ValueError, sqlite3.Error) as error:
            return True, assistant.t(f"Ingestion failed: {error}", f"Η εισαγωγή απέτυχε: {error}", language)
    if command == "/summarize":
        if not argument:
            return True, assistant.t("Usage: /summarize PATH", "Χρήση: /σύνοψη ΔΙΑΔΡΟΜΗ", language)
        try:
            path = Path(argument).expanduser().resolve()
            if not path.is_file():
                raise ValueError("path is not a file")
            if path.stat().st_size > MAX_FILE_BYTES:
                raise ValueError("file is too large")
            text = clean_document_text(decode_text_bytes(path.read_bytes()), path.suffix.casefold())
            if detect_language(text) == "unsupported":
                raise ValueError("file is not English or Greek")
            return True, extractive_summary(text, language, max_sentences=7)
        except (OSError, ValueError, UnicodeError) as error:
            return True, assistant.t(f"Summary failed: {error}", f"Η σύνοψη απέτυχε: {error}", language)
    if command in {"/dork", "/web-learn"}:
        if not argument:
            return True, assistant.t(
                "Usage: /dork public research query. Example: /dork site:python.org filetype:html sqlite tutorial",
                "Χρήση: /dork δημόσιο ερώτημα έρευνας. Παράδειγμα: /dork site:python.org sqlite tutorial",
                language
            )
        try:
            print(assistant.t("Searching and indexing public pages...", "Αναζήτηση και ευρετηρίαση δημόσιων σελίδων...", language), flush=True)
            result = assistant.web_research.learn(argument, max_pages=3)
            lines = [assistant.t(
                f"Web learning completed: {len(result['results'])} results, {result['pages']} pages fetched, {result['chunks']} knowledge chunks stored.",
                f"Η μάθηση από τον ιστό ολοκληρώθηκε: {len(result['results'])} αποτελέσματα, {result['pages']} σελίδες, {result['chunks']} τμήματα γνώσης αποθηκεύτηκαν.",
                language
            )]
            for item in result["results"][:5]:
                lines.append(f"  - {item['title']}\n    {item['url']}")
            if result["errors"]:
                lines.append(assistant.t(
                    f"Some pages were skipped ({len(result['errors'])}) because of robots, size, type, or network restrictions.",
                    f"Ορισμένες σελίδες παραλείφθηκαν ({len(result['errors'])}) λόγω robots, μεγέθους, τύπου ή περιορισμών δικτύου.",
                    language
                ))
            return True, "\n".join(lines)
        except (OSError, ValueError, PermissionError, TimeoutError, urllib.error.URLError) as error:
            return True, assistant.t(f"Web learning failed: {error}", f"Η μάθηση από τον ιστό απέτυχε: {error}", language)
    if command == "/llm":
        if not argument:
            return True, assistant.t(
                f"Current GGUF LLM mode: {assistant.llm_mode}. Use /llm off, /llm fallback, or /llm always.",
                f"Τρέχουσα λειτουργία GGUF LLM: {assistant.llm_mode}. Χρησιμοποίησε /llm off, /llm fallback ή /llm always.",
                language
            )
        try:
            assistant.set_llm_mode(argument)
            return True, assistant.t(f"GGUF LLM mode set to {assistant.llm_mode}.", f"Η λειτουργία GGUF LLM ορίστηκε σε {assistant.llm_mode}.", language)
        except ValueError as error:
            return True, assistant.t(str(error), "Η λειτουργία LLM πρέπει να είναι off, fallback ή always.", language)
    if command == "/llm-model":
        if not argument:
            return True, assistant.t(
                f"Active model: {assistant.local_llm.active_model}. Use /llm-model fast or /llm-model quality.",
                f"Ενεργό μοντέλο: {assistant.local_llm.active_model}. Χρησιμοποίησε /llm-model fast ή /llm-model quality.",
                language,
            )
        try:
            selected = assistant.set_llm_model(argument)
            return True, assistant.t(
                f"Active GGUF model set to {selected}. Only this model is loaded during a response.",
                f"Το ενεργό GGUF μοντέλο ορίστηκε σε {selected}. Μόνο αυτό φορτώνεται κατά την απάντηση.",
                language,
            )
        except ValueError as error:
            return True, assistant.t(str(error), f"Αποτυχία επιλογής μοντέλου: {error}", language)
    if command == "/cpu-profile":
        if not argument:
            runtime = assistant.local_llm.runtime_settings()
            return True, assistant.t(
                f"CPU profile: requested={assistant.local_llm.requested_cpu_profile}, active={runtime['resolved']}. Use auto, ultra_eco, eco, entry, balanced, or performance.",
                f"Profile επεξεργαστή: ζητήθηκε={assistant.local_llm.requested_cpu_profile}, ενεργό={runtime['resolved']}. Χρησιμοποίησε auto, ultra_eco, eco, entry, balanced ή performance.",
                language,
            )
        try:
            selected = assistant.set_llm_cpu_profile(argument)
            runtime = assistant.local_llm.runtime_settings()
            return True, assistant.t(
                f"CPU profile set to {selected}; active runtime is {runtime['resolved']} with {runtime['threads']} thread(s), context {runtime['context']}, batch {runtime['batch']}, and micro-batch {runtime['ubatch']}.",
                f"Το profile επεξεργαστή ορίστηκε σε {selected}. Η ενεργή ρύθμιση είναι {runtime['resolved']} με {runtime['threads']} νήμα/νήματα, context {runtime['context']}, batch {runtime['batch']} και micro-batch {runtime['ubatch']}.",
                language,
            )
        except ValueError as error:
            return True, assistant.t(str(error), "Το profile πρέπει να είναι auto, ultra_eco, eco, entry, balanced ή performance.", language)
    if command == "/llm-status":
        status = assistant.local_llm.status()
        runtime = status["runtime"]
        device = status["device"]
        device_name = device.get("model") or device.get("device") or "unknown"
        marker = device.get("processor_family") or "unknown"
        lines_en = [
            f"GGUF ready: {status['available']}",
            f"Active model: {status['active_model']}",
            f"Mode: {assistant.llm_mode}",
            f"llama.cpp: {status['binary']}",
            f"CPU profile: {status['cpu_profile_requested']} -> {status['cpu_profile_resolved']}",
            f"Runtime: threads={runtime['threads']}, context={runtime['context']}, batch={runtime['batch']}, ubatch={runtime['ubatch']}, token cap={runtime['max_tokens']}",
            f"Detected device: {device_name}; processor family={marker}; available RAM={human_size(runtime['available_ram'])}",
        ]
        lines_el = [
            f"GGUF έτοιμο: {status['available']}",
            f"Ενεργό μοντέλο: {status['active_model']}",
            f"Λειτουργία: {assistant.llm_mode}",
            f"llama.cpp: {status['binary']}",
            f"Profile επεξεργαστή: {status['cpu_profile_requested']} -> {status['cpu_profile_resolved']}",
            f"Ρυθμίσεις: νήματα={runtime['threads']}, context={runtime['context']}, batch={runtime['batch']}, ubatch={runtime['ubatch']}, όριο tokens={runtime['max_tokens']}",
            f"Συσκευή: {device_name}; οικογένεια επεξεργαστή={marker}; διαθέσιμη RAM={human_size(runtime['available_ram'])}",
        ]
        for key in ("fast", "quality"):
            item = status["models"][key]
            lines_en.append(f"{key}: {item['path']} | {human_size(item['size'])} | checksum={item['verified']}")
            lines_el.append(f"{key}: {item['path']} | {human_size(item['size'])} | checksum={item['verified']}")
        return True, "\n".join(lines_el if language == "el" else lines_en)
    if command == "/ask-llm":
        if not argument:
            return True, assistant.t("Usage: /ask-llm PROMPT", "Χρήση: /ask-llm PROMPT", language)
        if detect_language(argument) == "unsupported":
            return True, assistant.t("The prompt must be English or Greek.", "Το prompt πρέπει να είναι στα Αγγλικά ή στα Ελληνικά.", language)
        try:
            candidates = assistant.store.retrieve_many(argument, limit=5, language=language)
            response, _ = assistant.ask_local_llm(argument, language, candidates)
            return True, response
        except RuntimeError as error:
            return True, assistant.t(
                f"The selected local GGUF model is unavailable: {error}. Run Other Files/install_models.sh.",
                f"Το επιλεγμένο τοπικό GGUF μοντέλο δεν είναι διαθέσιμο: {error}. Τρέξε το Other Files/install_models.sh.",
                language
            )
    if command == "/remember":
        if "=" not in argument:
            return True, assistant.t("Usage: /remember KEY = VALUE", "Χρήση: /remember ΚΛΕΙΔΙ = ΤΙΜΗ", language)
        key, value = (part.strip() for part in argument.split("=", 1))
        if not key or not value:
            return True, assistant.t("Both key and value are required.", "Απαιτούνται κλειδί και τιμή.", language)
        if detect_language(key + " " + value) == "unsupported":
            return True, assistant.t("Memories must be English or Greek.", "Οι μνήμες πρέπει να είναι στα Αγγλικά ή στα Ελληνικά.", language)
        assistant.store.set_memory(key, value)
        return True, assistant.t(f"Remembered: {key} = {value}", f"Το θυμήθηκα: {key} = {value}", language)
    if command == "/memories":
        memories = assistant.store.list_memories()
        if not memories:
            return True, assistant.t("No persistent memories are stored.", "Δεν υπάρχουν αποθηκευμένες μνήμες.", language)
        title = assistant.t("Stored memories:", "Αποθηκευμένες μνήμες:", language)
        return True, title + "\n" + "\n".join(f"  {key} = {value}" for key, value in memories)
    if command == "/forget":
        if not argument:
            return True, assistant.t("Usage: /forget KEY", "Χρήση: /forget ΚΛΕΙΔΙ", language)
        removed = assistant.store.forget_memory(argument)
        return True, assistant.t(
            f"Forgot memory: {argument}" if removed else f"No memory named {argument!r} was found.",
            f"Διαγράφηκε η μνήμη: {argument}" if removed else f"Δεν βρέθηκε μνήμη με όνομα {argument!r}.",
            language
        )
    if command == "/train":
        try:
            assistant.retrain()
            return True, assistant.t("Neural model retrained and reloaded.\n", "Το νευρωνικό μοντέλο επανεκπαιδεύτηκε και φορτώθηκε.\n", language) + assistant.stats_text()
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
            return True, assistant.t(f"Training failed: {error}", f"Η εκπαίδευση απέτυχε: {error}", language)
    if command == "/build-lm":
        try:
            extra = Path(argument) if argument else None
            result = assistant.build_language_model(extra)
            return True, assistant.t(
                f"Language model built from {result['sentences']} sentences and {result['contexts']:,} contexts. Size: {human_size(result['size'])}.",
                f"Το γλωσσικό μοντέλο δημιουργήθηκε από {result['sentences']} προτάσεις και {result['contexts']:,} συμφραζόμενα. Μέγεθος: {human_size(result['size'])}.",
                language
            )
        except (OSError, ValueError, pickle.PickleError) as error:
            return True, assistant.t(f"Language-model build failed: {error}", f"Η δημιουργία γλωσσικού μοντέλου απέτυχε: {error}", language)
    if command == "/generate":
        if assistant.language_model is None:
            return True, assistant.t("Build the experimental generator first with /build-lm.", "Δημιούργησε πρώτα τον generator με /build-lm.", language)
        if argument and detect_language(argument) == "unsupported":
            return True, assistant.t("The prompt must be English or Greek.", "Το prompt πρέπει να είναι στα Αγγλικά ή στα Ελληνικά.", language)
        generated = assistant.language_model.generate(argument, max_words=52)
        if detect_language(generated) == "unsupported":
            return True, assistant.t("Generation was rejected by the language filter.", "Η παραγωγή απορρίφθηκε από το φίλτρο γλώσσας.", language)
        return True, generated
    if command == "/history":
        history = assistant.store.recent_history(16)
        if not history:
            return True, assistant.t("No saved history.", "Δεν υπάρχει αποθηκευμένο ιστορικό.", language)
        labels = {"user": assistant.t("User", "Χρήστης", language), "assistant": assistant.t("Assistant", "Βοηθός", language)}
        return True, "\n".join(f"{labels.get(role, role.title())}: {text}" for role, text in history)
    if command == "/clear-history":
        assistant.store.clear_history()
        assistant.session_history.clear()
        return True, assistant.t("Conversation history cleared.", "Το ιστορικό συνομιλίας διαγράφηκε.", language)
    if command == "/export":
        exports = assistant.data_dir / "exports"
        exports.mkdir(parents=True, exist_ok=True)
        path = exports / f"knowledge_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        assistant.store.export_json(path)
        return True, assistant.t(f"Exported local knowledge to {path}", f"Η τοπική γνώση εξήχθη στο {path}", language)
    if command == "/backup":
        try:
            assistant.store.connection.execute("PRAGMA wal_checkpoint(FULL)")
            path = create_backup(assistant.data_dir)
            return True, assistant.t(f"Backup created: {path} ({human_size(path.stat().st_size)})", f"Δημιουργήθηκε backup: {path} ({human_size(path.stat().st_size)})", language)
        except OSError as error:
            return True, assistant.t(f"Backup failed: {error}", f"Το backup απέτυχε: {error}", language)
    if command == "/benchmark":
        result = benchmark_assistant(assistant)
        return True, assistant.t(
            f"Neural inference: {result['neural_iterations']} predictions in {result['neural_seconds']:.3f}s ({result['neural_per_second']:.1f}/s)\nKnowledge retrieval: {result['retrieval_iterations']} searches in {result['retrieval_seconds']:.3f}s ({result['retrieval_per_second']:.1f}/s)",
            f"Νευρωνική πρόβλεψη: {result['neural_iterations']} προβλέψεις σε {result['neural_seconds']:.3f}s ({result['neural_per_second']:.1f}/s)\nΑνάκτηση γνώσης: {result['retrieval_iterations']} αναζητήσεις σε {result['retrieval_seconds']:.3f}s ({result['retrieval_per_second']:.1f}/s)",
            language
        )
    if command == "/profile":
        lines = [assistant.t(f"Current profile: {assistant.profile_name}", f"Τρέχον profile: {assistant.profile_name}", language)]
        for name, profile in MODEL_PROFILES.items():
            params = profile["hash_size"] * profile["hidden1"] + profile["hidden1"] * profile["hidden2"] + profile["hidden2"] * len(assistant.model.tags)
            lines.append(f"  {name:8s} {profile['hash_size']:5d} -> {profile['hidden1']:3d} -> {profile['hidden2']:2d}; approximately {params:,} weights. {profile['description']}")
        lines.append(assistant.t("Change profile by restarting with --profile NAME --train.", "Άλλαξε profile με επανεκκίνηση και --profile NAME --train.", language))
        return True, "\n".join(lines)
    return True, assistant.t("Unknown command. Type /help.", "Άγνωστη εντολή. Γράψε /βοήθεια.", language)

def chat_loop(assistant: PocketAssistant) -> None:
    if assistant.language_mode == "el":
        print(f"\n{assistant.assistant_name} είναι έτοιμο. Γράψε /βοήθεια για εντολές.")
    elif assistant.language_mode == "en":
        print(f"\n{assistant.assistant_name} is ready. Type /help for commands.")
    else:
        print(f"\n{assistant.assistant_name} is ready / είναι έτοιμο. Type /help or /βοήθεια.")
    while True:
        try:
            prompt = "Εσύ: " if assistant.last_language == "el" else "You: "
            text = input("\n" + prompt).strip()
        except (EOFError, KeyboardInterrupt):
            farewell = assistant.t("Goodbye.", "Αντίο.")
            print(f"\n{assistant.assistant_name}: {farewell}")
            return
        if not text:
            continue
        if text.startswith("/"):
            keep_running, message = handle_command(assistant, text)
            if message:
                print(message)
            if not keep_running:
                return
            continue
        response, details = assistant.answer(text)
        print(f"{assistant.assistant_name}: {response}")
        if assistant.debug:
            print("[debug] " + json.dumps(details, ensure_ascii=False, default=str))


# ---------------------------------------------------------------------------
# CLI and lifecycle
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Large practical offline AI assistant for Termux and older Android phones.",
        epilog=textwrap.dedent(
            """
            Profiles:
              micro     emergency minimum-memory classifier
              lite      fastest general low-memory classifier
              balanced  suitable for many 1.5-2.5 GB phones
              standard  stronger middle tier for roughly 3-4 GB phones
              max       largest bundled classifier for stronger phones
              extreme   optional local-training profile; not bundled pre-trained

            GGUF CPU presets:
              ultra_eco emergency mode for very low RAM or 32-bit userspace
              eco       safest for approximately 1.5-2 GB devices
              entry     entry-level Cortex-A53/A55 class
              balanced  mainstream mid-range phones
              performance modern mid-range and flagship phones
            """
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--train", action="store_true", help="Force neural retraining and exit.")
    mode.add_argument("--benchmark", action="store_true", help="Run local performance tests and exit.")
    mode.add_argument("--reset", action="store_true", help="Reset all PocketAI MAX data after confirmation.")
    mode.add_argument("--ingest", type=Path, help="Index a file or directory and exit.")
    mode.add_argument("--web-learn", type=str, help="Safely research and index a public English/Greek web query.")
    mode.add_argument("--scan-phone", action="store_true", help="Scan CPU, RAM, storage, and select the best bundled model.")
    parser.add_argument("--data", type=Path, default=default_data_dir(), help="Application data directory.")
    parser.add_argument(
        "--profile", choices=("auto", *MODEL_PROFILES.keys()), default="auto",
        help="Neural model profile. Default: auto."
    )
    parser.add_argument("--epochs", type=int, help="Override the profile's maximum training epochs.")
    parser.add_argument(
        "--cpu-profile", choices=("auto", *LLM_CPU_PROFILES.keys()),
        help="GGUF processor preset selected automatically from CPU, RAM, and storage.",
    )
    parser.add_argument(
        "--confidence", type=float, default=DEFAULT_CONFIDENCE,
        help=f"Minimum neural answer confidence. Default: {DEFAULT_CONFIDENCE}."
    )
    parser.add_argument("--yes", action="store_true", help="Skip reset confirmation.")
    return parser.parse_args()


def bootstrap_pretrained_model(
    dataset_path: Path,
    model_path: Path,
    metadata_path: Path,
    profile_name: str
) -> bool:
    """Install a bundled pre-trained classifier when it exactly matches the dataset."""
    if model_path.exists() or metadata_path.exists():
        return False
    bundled_profiles = {
        "micro": "pretrained_micro",
        "lite": "pretrained_lite",
        "balanced": "pretrained_balanced",
        "standard": "pretrained_standard",
        "max": "pretrained_max",
    }
    bundled_name = bundled_profiles.get(profile_name)
    if not bundled_name:
        return False
    bundled = Path(__file__).resolve().parent / "Models" / bundled_name
    bundled_model = bundled / "neural_model.pkl.gz"
    bundled_metadata = bundled / "model_metadata.json"
    if not bundled_model.is_file() or not bundled_metadata.is_file():
        return False
    try:
        metadata = load_json(bundled_metadata)
        if (
            metadata.get("model_version") != MODEL_VERSION
            or metadata.get("profile") != profile_name
            or metadata.get("dataset_sha256") != sha256_file(dataset_path)
        ):
            return False
        model_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(bundled_model, model_path)
        shutil.copy2(bundled_metadata, metadata_path)
        return True
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        for target in (model_path, metadata_path):
            try:
                target.unlink(missing_ok=True)
            except OSError:
                pass
        return False


def load_or_train_model(
    dataset_path: Path,
    model_path: Path,
    metadata_path: Path,
    profile_name: str,
    epochs_override: Optional[int],
    force: bool
) -> Tuple[DeepSparseClassifier, dict, dict]:
    dataset = validate_dataset(load_json(dataset_path))
    if not force and model_path.exists() and model_is_current(metadata_path, dataset_path, profile_name):
        try:
            model = load_model(model_path)
            metadata = load_json(metadata_path)
            return model, dataset, metadata
        except (OSError, ValueError, KeyError, TypeError, EOFError, pickle.PickleError) as error:
            print(f"Saved model could not be loaded: {error}")
            print("Rebuilding it locally.")
    return train_classifier(
        dataset_path, model_path, metadata_path, profile_name,
        epochs_override=epochs_override, verbose=True
    )


def reset_data(data_dir: Path, assume_yes: bool) -> int:
    if data_dir.exists() and not assume_yes:
        try:
            confirmation = input(f"Delete all PocketAI MAX data under {data_dir}? Type YES: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("Reset cancelled.")
            return 1
        if confirmation != "YES":
            print("Reset cancelled.")
            return 1
    if data_dir.exists():
        shutil.rmtree(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    ensure_dataset(data_dir / "dataset.json")
    print(f"Reset complete: {data_dir}")
    return 0


def main() -> int:
    args = parse_args()
    data_dir = args.data.expanduser().resolve()
    recommendation: Optional[dict] = None

    # With no command-line arguments, the program intentionally exposes only
    # the two requested top-level menu actions.
    if len(sys.argv) == 1:
        scan = launcher_menu(data_dir)
        if scan is None:
            return 0
        recommendation = scan.get("recommendation", {})
        args.profile = str(recommendation.get("classifier_profile", "balanced"))
        args.cpu_profile = str(recommendation.get("runtime_profile", "auto"))

    dataset_path = data_dir / "dataset.json"
    model_path = data_dir / "neural_model.pkl.gz"
    metadata_path = data_dir / "model_metadata.json"
    database_path = data_dir / "knowledge.sqlite3"
    language_model_path = data_dir / "language_model.pkl.gz"

    try:
        if args.reset:
            return reset_data(data_dir, args.yes)
        if getattr(args, "scan_phone", False):
            scan = scan_phone_hardware(data_dir, save=True, run_benchmark=True)
            print_phone_scan_report(scan)
            return 0

        data_dir.mkdir(parents=True, exist_ok=True)
        ensure_dataset(dataset_path)
        profile_name = choose_auto_profile() if args.profile == "auto" else args.profile
        print_banner(profile_name)
        profile = MODEL_PROFILES[profile_name]
        print(profile["description"])
        print(f"Data: {data_dir}")
        if recommendation:
            print(
                f"Automatic match: model={recommendation.get('gguf_model')}, "
                f"runtime={recommendation.get('runtime_profile')}, classifier={profile_name}."
            )
        if bootstrap_pretrained_model(dataset_path, model_path, metadata_path, profile_name):
            print("Installed a bundled pre-trained classifier.")

        model, dataset, metadata = load_or_train_model(
            dataset_path,
            model_path,
            metadata_path,
            profile_name,
            epochs_override=max(1, args.epochs) if args.epochs else None,
            force=args.train
        )

        assistant = PocketAssistant(
            data_dir=data_dir,
            dataset_path=dataset_path,
            model_path=model_path,
            metadata_path=metadata_path,
            database_path=database_path,
            language_model_path=language_model_path,
            model=model,
            dataset=dataset,
            metadata=metadata,
            profile_name=profile_name,
            confidence_threshold=max(0.10, min(0.95, args.confidence))
        )
        try:
            if args.cpu_profile:
                assistant.set_llm_cpu_profile(args.cpu_profile)
                runtime = assistant.local_llm.runtime_settings()
                print(
                    f"GGUF CPU profile: {args.cpu_profile} -> {runtime['resolved']} "
                    f"({runtime['threads']} thread(s), context {runtime['context']}, batch {runtime['batch']})."
                )
            if recommendation:
                selected_model = str(recommendation.get("gguf_model", "internal"))
                if selected_model in {"fast", "quality"}:
                    try:
                        assistant.set_llm_model(selected_model)
                        assistant.set_llm_mode("fallback")
                    except (OSError, ValueError) as error:
                        assistant.set_llm_mode("off")
                        print(f"Bundled GGUF runner unavailable; using the internal bilingual engine: {error}")
                else:
                    assistant.set_llm_mode("off")
            if args.train:
                print(assistant.stats_text())
                return 0
            if args.ingest:
                result = ingest_path(assistant.store, args.ingest)
                print(
                    f"Indexed {result['files_indexed']} files and {result['chunks_added']} chunks "
                    f"from {result['path']}."
                )
                return 0
            if args.web_learn:
                result = assistant.web_research.learn(args.web_learn, max_pages=3)
                print(
                    f"Web learning: {len(result['results'])} results, {result['pages']} pages, "
                    f"{result['chunks']} chunks stored."
                )
                return 0
            if args.benchmark:
                result = benchmark_assistant(assistant)
                print(
                    f"Neural: {result['neural_per_second']:.1f} predictions/s; "
                    f"retrieval: {result['retrieval_per_second']:.1f} searches/s."
                )
                print(assistant.stats_text())
                return 0
            chat_loop(assistant)
            return 0
        finally:
            assistant.close()

    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, sqlite3.Error) as error:
        print(f"Fatal error: {error}", file=sys.stderr)
        if os.environ.get("POCKETAI_DEBUG") == "1":
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
