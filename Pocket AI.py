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
- Safe no-key public-web research through Bing RSS, Wikipedia, and constrained search operators
- Optional SmolLM2 135M GGUF reasoning through llama.cpp
- Automatic RAM, storage, temperature, battery, and processor-aware model profiles
- Sequential hybrid inference with adaptive, expert, consensus, and cascade modes
- Persistent custom AI name and human-style bilingual conversation profiles
- Modular context optimization, confidence calibration, universal knowledge, WordNet lexical retrieval, offline encyclopedia retrieval, natural dialogue, and continuous resource tuning

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


# Optional standard-library runtime modules bundled under Other Files/Modules.
# Pocket AI remains usable with conservative fallbacks if a module file is
# damaged or removed.
RUNTIME_MODULE_DIR = Path(__file__).resolve().parent / "Other Files" / "Modules"
if str(RUNTIME_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_MODULE_DIR))
try:
    from persona_engine import (
        DEFAULT_PERSONA, PERSONA_STYLES, describe_persona, load_persona,
        naturalize_response, persona_instruction, sanitize_name, save_persona,
    )
except Exception:
    DEFAULT_PERSONA = {"assistant_name": "Pocket AI", "user_name": "", "style": "friendly", "human_style": True}
    PERSONA_STYLES = {"friendly": {"label_en": "Friendly", "label_el": "Φιλικό"}}
    def load_persona(data_dir: Path) -> dict: return dict(DEFAULT_PERSONA)
    def save_persona(data_dir: Path, payload: dict) -> dict: return dict(payload)
    def sanitize_name(value: str, fallback: str = "Pocket AI", maximum: int = 28) -> str: return str(value).strip()[:maximum] or fallback
    def persona_instruction(config: dict, language: str) -> str: return "Speak naturally and clearly while identifying as an AI assistant."
    def naturalize_response(text: str, language: str, config: dict, route: str = "", seed_text: str = "") -> str: return text.strip()
    def describe_persona(config: dict, language: str = "en") -> str: return f"AI name: {config.get('assistant_name', 'Pocket AI')}"
try:
    from context_optimizer import optimize_context
except Exception:
    optimize_context = None
try:
    from consensus_engine import choose_consensus
except Exception:
    choose_consensus = None
try:
    from confidence_engine import calibrate as calibrate_confidence
except Exception:
    def calibrate_confidence(details: dict, response: str) -> dict: return {"score": 0.5, "label": "medium"}
try:
    from resource_advisor import concise_reason as resource_reason
except Exception:
    def resource_reason(scan: dict, recommendation: dict, language: str = "en") -> str: return ""
try:
    from school_tutor import SchoolTutor
except Exception:
    class SchoolTutor:
        def __init__(self, knowledge_path: Path) -> None: self.path = Path(knowledge_path)
        def answer(self, text: str, language: str = "en") -> Optional[dict]: return None
        def catalog(self, language: str = "en") -> str:
            return "School foundation unavailable." if language != "el" else "Η σχολική βάση δεν είναι διαθέσιμη."
        def grade_overview(self, grade: int, subject: str, language: str = "en") -> str: return self.catalog(language)
        def instruction(self, language: str = "en") -> str: return "Explain school questions carefully."
        def close(self) -> None: return None
try:
    from universal_knowledge import UniversalKnowledge
except Exception:
    class UniversalKnowledge:
        def __init__(self, path: Path) -> None: self.path = Path(path); self.last_topic = ""
        def answer(self, text: str, language: str = "en") -> Optional[dict]: return None
        def answer_topic(self, topic_id: str, language: str = "en") -> Optional[dict]: return None
        def catalog(self, language: str = "en") -> str: return "Universal knowledge unavailable."
try:
    from lexical_knowledge import LexicalKnowledge
except Exception:
    class LexicalKnowledge:
        def __init__(self, directory: Path) -> None:
            self.directory = Path(directory); self.entry_count = 0; self.greek_count = 0
        @property
        def available(self) -> bool: return False
        def answer(self, text: str, language: str = "en") -> Optional[dict]: return None
        def context(self, text: str, language: str = "en", limit: int = 7, max_chars: int = 3000) -> str: return ""
        def catalog(self, language: str = "en") -> str:
            return "Lexical knowledge unavailable." if language != "el" else "Η λεξιλογική γνώση δεν είναι διαθέσιμη."
        def close(self) -> None: return None
try:
    from encyclopedia_knowledge import EncyclopediaKnowledge
except Exception:
    class EncyclopediaKnowledge:
        def __init__(self, directory: Path) -> None:
            self.directory = Path(directory); self.article_count = 0; self.chunk_count = 0; self.character_count = 0
        @property
        def available(self) -> bool: return False
        def answer(self, query: str, language: str = "en") -> Optional[dict]: return None
        def context(self, query: str, language: str = "en", limit: int = 6, max_chars: int = 2800) -> str: return ""
        def catalog(self, language: str = "en") -> str:
            return "Offline encyclopedia unavailable." if language != "el" else "Η offline εγκυκλοπαίδεια δεν είναι διαθέσιμη."
        def close(self) -> None: return None
try:
    from conversation_engine import ConversationEngine
except Exception:
    class ConversationEngine:
        def __init__(self) -> None: self.last_topic = ""
        def social_reply(self, text: str, language: str, assistant_name: str, user_name: str = "") -> Optional[str]: return None
        def contextualize(self, text: str, history, language: str, last_topic: str = "") -> Tuple[str, bool]: return text, False
        def instruction(self, text: str, language: str) -> str: return "Speak naturally and follow the user's intent."
try:
    from resource_matrix import optimize_runtime as optimize_phone_runtime, recommend_configuration as recommend_phone_configuration, COMBINATION_TIERS
except Exception:
    optimize_phone_runtime = None
    recommend_phone_configuration = None
    COMBINATION_TIERS = []
try:
    from smart_reasoning import (
        analyze_query as analyze_smart_query,
        build_evidence_packet,
        clean_answer as smart_clean_answer,
        extractive_fallback as smart_extractive_fallback,
        should_synthesize as smart_should_synthesize,
        validate_answer as validate_smart_answer,
    )
except Exception:
    def analyze_smart_query(text: str, language: str = "en") -> dict:
        return {"task": "general_question", "complexity": 0.5, "direct_ok": False, "use_llm": True, "style_instruction": "Answer directly and carefully."}
    def build_evidence_packet(query: str, sources, language: str = "en", task_profile=None, max_chars: int = 4200):
        rows=[]
        for index, source in enumerate(sources[:8], 1):
            text=str(source.get("text") or source.get("response") or "").strip()
            if text: rows.append(f"[E{index}] {source.get('title') or source.get('source') or 'Evidence'}: {text[:700]}")
        packet="\n".join(rows)[:max_chars]
        return packet, []
    def smart_clean_answer(text: str) -> str: return str(text).strip()
    def smart_extractive_fallback(query: str, ranked_evidence, language: str = "en", task_profile=None, max_sentences: int = 5) -> str: return ""
    def smart_should_synthesize(task_profile: dict, evidence, language: str = "en") -> bool: return True
    def validate_smart_answer(answer: str, question: str, language: str = "en") -> dict: return {"score": 0.5, "issues": []}
try:
    from advanced_reasoning import (
        audit_answer as audit_advanced_answer,
        build_reasoning_brief as build_advanced_reasoning_brief,
        choose_or_repair_answer as choose_advanced_answer,
        solve_tool_query as solve_advanced_tool_query,
        synthesize_grounded_answer as synthesize_advanced_answer,
    )
except Exception:
    def solve_advanced_tool_query(text: str, language: str = "en"): return None
    def synthesize_advanced_answer(query: str, evidence, language: str = "en", task_profile=None, max_sentences: int = 6):
        return {"response": "", "confidence": 0.0, "route": "advanced_unavailable"}
    def build_advanced_reasoning_brief(query: str, language: str, task_profile, evidence, deterministic_draft: str = "", max_chars: int = 1800):
        return "", {"plan": {}, "diagnostics": {}}
    def audit_advanced_answer(answer: str, question: str, evidence=(), language: str = "en", task_profile=None):
        return {"score": 0.5, "issues": []}
    def choose_advanced_answer(generated: str, grounded: str, audit, language: str = "en"):
        return generated or grounded, {"decision": "fallback"}


APP_NAME = "PocketAI Bilingual MAX"
MODEL_VERSION = 8
DATASET_VERSION = 6
RANDOM_SEED = 1121
DEFAULT_CONFIDENCE = 0.42
MAX_INPUT_CHARS = 4000
# The model subprocess is always bounded below two minutes. A few seconds are
# reserved for retrieval, prompt construction, cleanup, and safe fallback.
MAX_ANSWER_SECONDS = 112.0
MAX_LLM_CALL_SECONDS = 106.0
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
        "context": 1024,
        "batch": 64,
        "max_tokens": 224,
        "family": "smollm2",
    },
    "quality": {
        "filename": "SmolLM2-135M-Instruct.Q4_1.gguf",
        "sha256": "b179c9523d0e6a0f98a330c7562b682750a6f8c8c15e5bc70ea373728110db53",
        "label": "SmolLM2 135M Q4_1 (higher quality emergency model)",
        "context": 1536,
        "batch": 64,
        "max_tokens": 320,
        "family": "smollm2",
    },
    "smart": {
        "filename": "Qwen3-0.6B-Q8_0.gguf",
        "sha256": "",
        "label": "Qwen3 0.6B Q8_0 (recommended reasoning model)",
        "context": 4096,
        "batch": 64,
        "max_tokens": 512,
        "family": "qwen3",
        "source_repo": "Qwen/Qwen3-0.6B-GGUF",
        "quantization": "Q8_0",
        "verification": "official HTTPS source + local SHA-256 sidecar",
        "download_url": "https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/resolve/main/Qwen3-0.6B-Q8_0.gguf?download=true",
    },
    "ultra": {
        "filename": "Qwen3-1.7B-Q8_0.gguf",
        "sha256": "",
        "label": "Qwen3 1.7B Q8_0 (strongest guarded phone tier)",
        "context": 4096,
        "batch": 48,
        "max_tokens": 512,
        "family": "qwen3",
        "source_repo": "Qwen/Qwen3-1.7B-GGUF",
        "quantization": "Q8_0",
        "verification": "official HTTPS source + local SHA-256 sidecar",
        "download_url": "https://huggingface.co/Qwen/Qwen3-1.7B-GGUF/resolve/main/Qwen3-1.7B-Q8_0.gguf?download=true",
    },
}
DEFAULT_EXTERNAL_LLM_MODEL = "smart"
SPLIT_GGUF_DIRNAME = "GGUF Parts"
SPLIT_GGUF_MANIFEST = "split_models_manifest.json"
GGUF_CACHE_DIRNAME = "GGUF Models"
MAX_PACKAGED_MODEL_PART_BYTES = 60_000_000

LLM_CPU_PROFILES = {
    "ultra_eco": {
        "threads": 1,
        "context": {"fast": 384, "quality": 384, "smart": 384, "ultra": 256},
        "batch": 8,
        "ubatch": 8,
        "max_tokens": {"fast": 72, "quality": 80, "smart": 72, "ultra": 48},
        "timeout": 106,
        "description": "Emergency profile for very low free RAM, 32-bit userspace, or extremely slow processors.",
    },
    "eco": {
        "threads": 1,
        "context": {"fast": 512, "quality": 512, "smart": 512, "ultra": 384},
        "batch": 16,
        "ubatch": 8,
        "max_tokens": {"fast": 96, "quality": 112, "smart": 104, "ultra": 72},
        "timeout": 106,
        "description": "Minimum-memory profile for roughly 1.5-2 GB devices and heavily throttled processors.",
    },
    "entry": {
        "threads": 2,
        "context": {"fast": 768, "quality": 768, "smart": 768, "ultra": 640},
        "batch": 32,
        "ubatch": 16,
        "max_tokens": {"fast": 144, "quality": 168, "smart": 160, "ultra": 112},
        "timeout": 104,
        "description": "Entry-level profile for Cortex-A53/A55 phones such as Galaxy A12-class devices.",
    },
    "balanced": {
        "threads": 3,
        "context": {"fast": 1024, "quality": 1280, "smart": 1280, "ultra": 1024},
        "batch": 48,
        "ubatch": 32,
        "max_tokens": {"fast": 208, "quality": 256, "smart": 256, "ultra": 192},
        "timeout": 102,
        "description": "Balanced profile for mainstream 3-4 GB phones and efficient mid-range processors.",
    },
    "performance": {
        "threads": 4,
        "context": {"fast": 1024, "quality": 1536, "smart": 2048, "ultra": 2048},
        "batch": 64,
        "ubatch": 48,
        "max_tokens": {"fast": 224, "quality": 320, "smart": 384, "ultra": 320},
        "timeout": 100,
        "description": "Quality-first profile for modern mid-range and flagship processors with comfortable free RAM.",
    },
}
DEFAULT_LLM_CPU_PROFILE = "auto"

HYBRID_MODES = {
    "off": "Internal classifier, retrieval, tools, and specialists only.",
    "speed": "Use the lowest-memory GGUF model for fast single-pass answers.",
    "smart": "Route each question to the strongest safe installed model with one guarded pass.",
    "quality": "Prefer Qwen3 1.7B, then Qwen3 0.6B, when resources are safe.",
    "adaptive": "Use a smaller draft and a stronger verification pass only when resources and time permit.",
    "expert": "Use specialist guidance, optimized evidence, and the strongest safe Qwen model for technical questions.",
    "consensus": "Generate two sequential answers with different model tiers and select the stronger result.",
    "cascade": "Generate a compact draft, unload it, then verify and rewrite with a stronger model.",
    "auto": "Select speed, smart, quality, adaptive, or cascade from the live phone state.",
}
HYBRID_MODES_EL = {
    "off": "Μόνο εσωτερικός classifier, ανάκτηση, εργαλεία και specialists.",
    "speed": "Χρήση του μοντέλου με τη χαμηλότερη κατανάλωση RAM για γρήγορη απάντηση.",
    "smart": "Επιλογή του ισχυρότερου ασφαλούς εγκατεστημένου μοντέλου με ένα ελεγχόμενο πέρασμα.",
    "quality": "Προτίμηση Qwen3 1.7B και μετά Qwen3 0.6B όταν οι πόροι είναι ασφαλείς.",
    "adaptive": "Ξεκινά γρήγορα και εκτελεί ποιοτικό δεύτερο πέρασμα μόνο όταν χρειάζεται.",
    "expert": "Χρήση specialist, βελτιστοποιημένων συμφραζομένων και ποιοτικού μοντέλου για τεχνικές ερωτήσεις.",
    "consensus": "Δημιουργία ανεξάρτητων απαντήσεων Fast και Quality διαδοχικά και επιλογή της ισχυρότερης.",
    "cascade": "Γρήγορο πρόχειρο και μετά ξεχωριστός ποιοτικός έλεγχος και επανεγγραφή.",
    "auto": "Επιλογή speed, smart, quality, adaptive ή cascade από τη ζωντανή κατάσταση του κινητού.",
}
DEFAULT_HYBRID_MODE = "auto"

HYBRID_COMPONENT_FILES = {
    "router": "PocketAI_Hybrid_Router.json.gz",
    "planner": "PocketAI_Query_Planner.json.gz",
    "verifier": "PocketAI_Response_Verifier.json.gz",
    "resource_guard": "PocketAI_Resource_Guard.json.gz",
    "adaptive": "PocketAI_Adaptive_Controller.json.gz",
    "consensus": "PocketAI_Consensus_Controller.json.gz",
    "persona": "PocketAI_Persona_Controller.json.gz",
    "context": "PocketAI_Context_Optimizer.json.gz",
    "confidence": "PocketAI_Confidence_Calibrator.json.gz",
    "school_hybrid": "PocketAI_School_Hybrid_Controller.json.gz",
    "web_learning": "PocketAI_NoKey_Web_Learner.json.gz",
    "universal_knowledge": "PocketAI_Universal_Knowledge_Controller.json.gz",
    "natural_dialogue": "PocketAI_Natural_Dialogue_Controller.json.gz",
    "continuous_runtime": "PocketAI_Continuous_Runtime_Controller.json.gz",
    "knowledge_retriever": "PocketAI_Knowledge_Retriever.json.gz",
    "knowledge_reranker": "PocketAI_Knowledge_Reranker.json.gz",
    "knowledge_bridge": "PocketAI_CrossModel_Knowledge_Bridge.json.gz",
    "response_cache": "PocketAI_Response_Cache_Controller.json.gz",
    "prompt_compressor": "PocketAI_Prompt_Compressor.json.gz",
}

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
    "smart": {
        "label": "Qwen3 0.6B Q8_0 Smart",
        "minimum_total_ram": 3400 * 1024 ** 2,
        "minimum_available_ram": 900 * 1024 ** 2,
        "minimum_free_storage": 1100 * 1024 ** 2,
        "minimum_cpu_score": 22,
        "requires_64_bit": True,
        "processor_combos": "Recommended for capable 4 GB+ 64-bit phones. Entry-level devices use short context, non-thinking mode, and one guarded pass to protect the two-minute target.",
    },
    "ultra": {
        "label": "Qwen3 1.7B Q8_0 Ultra",
        "minimum_total_ram": 7000 * 1024 ** 2,
        "minimum_available_ram": 2500 * 1024 ** 2,
        "minimum_free_storage": 2800 * 1024 ** 2,
        "minimum_cpu_score": 48,
        "requires_64_bit": True,
        "processor_combos": "Strongest optional tier for capable 8 GB-class phones. It uses evidence-dense prompts, adaptive thinking, and strict output/deadline guards.",
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
        "I do not have a reliable local answer for that yet. Type help and choose Teach AI or Learn from a file.",
        "I am uncertain. Try a more specific question, or type help to add knowledge.",
        "That is outside my current model and indexed memory. Type help for learning options."
    ],
    "el": [
        "Δεν έχω ακόμη αξιόπιστη τοπική απάντηση. Γράψε βοήθεια και επίλεξε εκμάθηση ή αρχείο.",
        "Δεν είμαι βέβαιο. Κάνε πιο συγκεκριμένη ερώτηση ή γράψε βοήθεια για να προσθέσεις γνώση.",
        "Αυτό βρίσκεται έξω από το τρέχον μοντέλο και την ευρετηριασμένη μνήμη μου. Γράψε βοήθεια για επιλογές μάθησης."
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


def _read_integer(path: Path) -> int:
    try:
        return int(path.read_text(encoding="utf-8", errors="replace").strip())
    except (OSError, ValueError):
        return 0


def _temperature_celsius(raw: int) -> float:
    value = float(raw)
    if abs(value) >= 1000:
        value /= 1000.0
    elif abs(value) >= 200:
        value /= 10.0
    return value if -30.0 <= value <= 150.0 else 0.0


def _thermal_snapshot() -> dict:
    readings: List[dict] = []
    for zone in sorted(Path("/sys/class/thermal").glob("thermal_zone*")):
        raw = _read_integer(zone / "temp")
        value = _temperature_celsius(raw)
        if value <= 0:
            continue
        zone_type = _read_text_file(zone / "type", 120) or zone.name
        readings.append({"zone": zone.name, "type": zone_type, "celsius": round(value, 1)})
    battery_temp = _temperature_celsius(_read_integer(Path("/sys/class/power_supply/battery/temp")))
    if battery_temp > 0:
        readings.append({"zone": "battery", "type": "battery", "celsius": round(battery_temp, 1)})
    plausible = [item["celsius"] for item in readings if 10.0 <= float(item["celsius"]) <= 105.0]
    maximum = max(plausible) if plausible else 0.0
    if maximum >= 52.0:
        state = "critical"
    elif maximum >= 46.0:
        state = "hot"
    elif maximum >= 41.0:
        state = "warm"
    else:
        state = "normal"
    return {"maximum_celsius": round(maximum, 1), "state": state, "readings": readings[:24]}


def _battery_snapshot() -> dict:
    base = Path("/sys/class/power_supply/battery")
    capacity = _read_integer(base / "capacity")
    status = _read_text_file(base / "status", 80)
    health = _read_text_file(base / "health", 80)
    current_now = _read_integer(base / "current_now")
    power_save = _android_property("power.save.mode") or _android_property("persist.sys.powersave")
    return {
        "capacity_percent": max(0, min(100, capacity)) if capacity else 0,
        "status": status or "unknown",
        "health": health or "unknown",
        "current_now": current_now,
        "power_save": str(power_save).casefold() in {"1", "true", "on", "yes"},
    }


def _split_gguf_manifest(script_dir: Path) -> dict:
    path = script_dir / "Models" / SPLIT_GGUF_DIRNAME / SPLIT_GGUF_MANIFEST
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def _split_gguf_parts(script_dir: Path, filename: str) -> Tuple[List[Path], dict]:
    manifest = _split_gguf_manifest(script_dir)
    models = manifest.get("models", {}) if isinstance(manifest, dict) else {}
    entry = models.get(filename, {}) if isinstance(models, dict) else {}
    rows = entry.get("parts", []) if isinstance(entry, dict) else []
    base = script_dir / "Models" / SPLIT_GGUF_DIRNAME
    parts: List[Path] = []
    if not isinstance(rows, list) or not rows:
        return parts, {}
    for row in rows:
        if not isinstance(row, dict):
            return [], {}
        name = str(row.get("file", ""))
        if not name or Path(name).name != name:
            return [], {}
        path = base / name
        try:
            expected_size = int(row.get("size_bytes", 0) or 0)
            if not path.is_file() or expected_size <= 0 or path.stat().st_size != expected_size:
                return [], {}
            if path.stat().st_size > MAX_PACKAGED_MODEL_PART_BYTES:
                return [], {}
        except OSError:
            return [], {}
        parts.append(path)
    return parts, entry


def _hash_concatenated_files(paths: Sequence[Path], verify_part_hashes: Optional[Sequence[str]] = None) -> str:
    combined = hashlib.sha256()
    for index, path in enumerate(paths):
        part_hash = hashlib.sha256()
        with path.open("rb") as handle:
            while True:
                block = handle.read(1024 * 1024)
                if not block:
                    break
                combined.update(block)
                if verify_part_hashes is not None:
                    part_hash.update(block)
        if verify_part_hashes is not None:
            expected = str(verify_part_hashes[index]).casefold()
            if not expected or part_hash.hexdigest().casefold() != expected:
                raise ValueError(f"Split model part checksum mismatch: {path.name}")
    return combined.hexdigest()


def _split_gguf_status(script_dir: Path, filename: str, expected_sha256: str, verify_hashes: bool = False) -> dict:
    parts, entry = _split_gguf_parts(script_dir, filename)
    complete = bool(parts)
    size = sum(path.stat().st_size for path in parts) if complete else 0
    expected_size = int(entry.get("size_bytes", 0) or 0) if entry else 0
    header_valid = False
    if complete:
        try:
            with parts[0].open("rb") as handle:
                header_valid = handle.read(4) == b"GGUF"
        except OSError:
            header_valid = False
    digest = ""
    verified = False
    if complete and verify_hashes:
        rows = entry.get("parts", [])
        part_hashes = [str(row.get("sha256", "")) for row in rows]
        try:
            digest = _hash_concatenated_files(parts, part_hashes)
            verified = digest == expected_sha256 and size == expected_size
        except (OSError, ValueError, IndexError):
            digest = ""
            verified = False
    return {
        "complete": complete and size == expected_size,
        "parts": [str(path) for path in parts],
        "part_count": len(parts),
        "size": size,
        "expected_size": expected_size,
        "header_valid": header_valid,
        "sha256": digest,
        "verified": verified,
    }


def _materialize_split_gguf(script_dir: Path, data_dir: Path, filename: str, expected_sha256: str) -> Path:
    parts, entry = _split_gguf_parts(script_dir, filename)
    if not parts:
        raise FileNotFoundError(f"The packaged parts for {filename} are missing or incomplete.")
    expected_size = int(entry.get("size_bytes", 0) or 0)
    if expected_size <= 0:
        raise ValueError(f"Invalid split-model manifest entry for {filename}.")
    target_dir = data_dir / GGUF_CACHE_DIRNAME
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / filename
    state_path = target_dir / f"{filename}.reconstructed.json"

    try:
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
    except (OSError, ValueError, TypeError):
        state = {}
    if target.is_file():
        try:
            if (
                target.stat().st_size == expected_size
                and _gguf_header_valid(target)
                and state.get("sha256") == expected_sha256
                and state.get("size_bytes") == expected_size
                and int(state.get("mtime_ns", -1)) == target.stat().st_mtime_ns
            ):
                return target
        except OSError:
            pass

    try:
        free_bytes = shutil.disk_usage(target_dir).free
    except OSError:
        free_bytes = expected_size * 2
    if free_bytes < expected_size + 32 * 1024 * 1024:
        raise OSError(
            f"Not enough free storage to reconstruct {filename}. "
            f"At least {human_size(expected_size + 32 * 1024 * 1024)} is required."
        )

    temp = target_dir / f".{filename}.{os.getpid()}.tmp"
    rows = entry.get("parts", [])
    expected_part_hashes = [str(row.get("sha256", "")) for row in rows]
    combined = hashlib.sha256()
    written = 0
    try:
        with temp.open("wb") as output:
            for index, part in enumerate(parts):
                part_hash = hashlib.sha256()
                with part.open("rb") as source:
                    while True:
                        block = source.read(1024 * 1024)
                        if not block:
                            break
                        output.write(block)
                        combined.update(block)
                        part_hash.update(block)
                        written += len(block)
                if part_hash.hexdigest() != expected_part_hashes[index]:
                    raise ValueError(f"Split model part checksum mismatch: {part.name}")
            output.flush()
            os.fsync(output.fileno())
        digest = combined.hexdigest()
        if written != expected_size or digest != expected_sha256 or not _gguf_header_valid(temp):
            raise ValueError(f"Reconstructed model verification failed: {filename}")
        os.replace(temp, target)
        target_mtime_ns = target.stat().st_mtime_ns
        state_path.write_text(
            json.dumps({
                "filename": filename,
                "size_bytes": expected_size,
                "sha256": digest,
                "mtime_ns": target_mtime_ns,
                "parts": [path.name for path in parts],
                "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            }, indent=2) + "\n",
            encoding="utf-8",
        )
        return target
    finally:
        try:
            if temp.exists():
                temp.unlink()
        except OSError:
            pass


def _gguf_header_valid(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return handle.read(4) == b"GGUF"
    except OSError:
        return False


def _resource_pressure(scan: dict) -> dict:
    total = int(scan.get("ram", {}).get("total", 0) or 0)
    available = int(scan.get("ram", {}).get("available", 0) or 0)
    ratio = available / total if total else 0.0
    free_storage = int(scan.get("storage", {}).get("runtime", {}).get("free", 0) or 0)
    temperature = float(scan.get("thermal", {}).get("maximum_celsius", 0.0) or 0.0)
    battery = scan.get("battery", {})
    score = 0
    reasons: List[str] = []
    if available and available < 240 * 1024 ** 2:
        score += 4; reasons.append("very low available RAM")
    elif available and available < 420 * 1024 ** 2:
        score += 2; reasons.append("low available RAM")
    if ratio and ratio < 0.12:
        score += 2; reasons.append("Android is using most RAM")
    if free_storage and free_storage < 300 * 1024 ** 2:
        score += 2; reasons.append("low free application storage")
    if temperature >= 52:
        score += 5; reasons.append("critical temperature")
    elif temperature >= 46:
        score += 3; reasons.append("high temperature")
    elif temperature >= 41:
        score += 1; reasons.append("warm device")
    if bool(battery.get("power_save")):
        score += 1; reasons.append("power saving is active")
    level = int(battery.get("capacity_percent", 0) or 0)
    status = str(battery.get("status", "")).casefold()
    if level and level <= 12 and "charging" not in status:
        score += 1; reasons.append("battery is low")
    return {"score": score, "reasons": reasons, "ram_ratio": ratio}


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


def _model_path_status(script_dir: Path, verify_hashes: bool = False) -> dict:
    result: Dict[str, dict] = {}
    for model_id, config in EXTERNAL_LLM_MODELS.items():
        path = script_dir / "Models" / str(config["filename"])
        direct_exists = path.is_file()
        digest = ""
        split = _split_gguf_status(
            script_dir,
            str(config["filename"]),
            str(config["sha256"]),
            verify_hashes=verify_hashes,
        )
        exists = direct_exists or bool(split.get("complete"))
        if direct_exists and verify_hashes:
            try:
                digest = sha256_file(path)
            except OSError:
                digest = ""
        elif split.get("complete") and verify_hashes:
            digest = str(split.get("sha256", ""))
        size = path.stat().st_size if direct_exists else int(split.get("size", 0) or 0)
        header_valid = _gguf_header_valid(path) if direct_exists else bool(split.get("header_valid"))
        result[model_id] = {
            "path": str(path) if direct_exists else str(script_dir / "Models" / SPLIT_GGUF_DIRNAME),
            "exists": exists,
            "materialized": direct_exists,
            "split_package": bool(split.get("complete")),
            "part_count": int(split.get("part_count", 0) or 0),
            "size": size,
            "header_valid": header_valid,
            "expected_sha256": str(config["sha256"]),
            "sha256": digest,
            "verified": bool(digest) and digest == str(config["sha256"]),
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
    if model_id in EXTERNAL_LLM_MODELS:
        model_state = scan["models"][model_id]
        if not model_state["exists"]:
            reasons.append("model file is missing")
        elif not model_state.get("header_valid", False):
            reasons.append("model has an invalid GGUF header")
        elif model_state.get("sha256") and not model_state.get("verified", False):
            reasons.append("model checksum does not match")
    return not reasons, reasons


def _recommend_ai_configuration(scan: dict) -> dict:
    """Choose the strongest safe stack from live CPU, RAM, storage, bitness, and heat."""
    compatibility: Dict[str, dict] = {}
    for model_id in AI_MODEL_COMPATIBILITY:
        compatible, reasons = _check_model_compatibility(model_id, scan)
        compatibility[model_id] = {"compatible": compatible, "reasons": reasons}

    if recommend_phone_configuration is not None:
        selected = recommend_phone_configuration(scan, compatibility)
    else:
        fallback_model = next((name for name in ("ultra", "smart", "quality", "fast") if compatibility.get(name, {}).get("compatible")), "internal")
        selected = {
            "gguf_model": fallback_model,
            "classifier_profile": "balanced",
            "runtime_profile": "entry",
            "runtime_combination": "fallback",
            "runtime_plan": {},
            "hybrid_mode": "smart",
            "llm_mode": "always",
            "selection_reasons": ["conservative fallback selection"],
        }

    classifier = str(selected.get("classifier_profile", "balanced"))
    script_dir = Path(__file__).resolve().parent
    fallback_order = {
        "max": ("max", "standard", "balanced", "lite", "micro"),
        "standard": ("standard", "balanced", "lite", "micro"),
        "balanced": ("balanced", "lite", "micro"),
        "lite": ("lite", "micro"),
        "micro": ("micro",),
    }
    for candidate in fallback_order.get(classifier, ("balanced", "lite", "micro")):
        bundled = script_dir / "Models" / f"pretrained_{candidate}" / "neural_model.pkl.gz"
        if bundled.is_file():
            classifier = candidate
            break

    pressure = _resource_pressure(scan)
    selected.update({
        "classifier_profile": classifier,
        "confidence": "high" if selected.get("gguf_model") != "internal" and pressure["score"] <= 1 else "medium",
        "resource_pressure": pressure,
        "compatibility": compatibility,
    })
    return selected


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
    thermal = _thermal_snapshot()
    battery = _battery_snapshot()

    scan = {
        "schema_version": 2,
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
        "thermal": thermal,
        "battery": battery,
        "models": _model_path_status(script_dir, verify_hashes=run_benchmark),
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
        return profile if isinstance(profile, dict) and profile.get("schema_version") in {1, 2} else None
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
    thermal = scan.get("thermal", {})
    battery = scan.get("battery", {})
    if thermal.get("maximum_celsius"):
        print(f"Temperature: {thermal['maximum_celsius']:.1f}°C ({thermal.get('state', 'unknown')})")
    if battery.get("capacity_percent"):
        print(f"Battery: {battery['capacity_percent']}% / {battery.get('status', 'unknown')} / health {battery.get('health', 'unknown')}")
    storage = scan["storage"]["runtime"]
    print(f"Application storage: {human_size(storage['free'])} free of {human_size(storage['total'])}")
    shared = scan["storage"]["shared_downloads"]
    if shared["total"]:
        print(f"Shared Downloads storage: {human_size(shared['free'])} free of {human_size(shared['total'])}")
    print("\nModel compatibility:")
    for model_id in ("internal", "fast", "quality", "smart", "ultra"):
        print(_compatibility_line(model_id, scan))
    print("\nBundled / optional model integrity:")
    for model_id in ("fast", "quality", "smart", "ultra"):
        item = scan.get("models", {}).get(model_id, {})
        checksum = "verified" if item.get("verified") else "not checked" if not item.get("sha256") else "FAILED"
        print(f"  {model_id}: header={'valid' if item.get('header_valid') else 'invalid'}; checksum={checksum}; size={human_size(int(item.get('size', 0) or 0))}")
    print("\nBest automatic match:")
    print(f"  AI model: {recommendation['gguf_model']}")
    print(f"  Neural classifier: {recommendation['classifier_profile']}")
    print(f"  CPU/RAM runtime: {recommendation['runtime_profile']}")
    if recommendation.get("runtime_combination"):
        print(f"  Hardware combination: {recommendation['runtime_combination']}")
    plan = recommendation.get("runtime_plan") or {}
    if plan:
        print(f"  Tuned inference: {plan.get('threads')} thread(s), context {plan.get('context')}, batch {plan.get('batch')}, output {plan.get('max_tokens')} tokens")
    print(f"  Local LLM mode: {recommendation['llm_mode']}")
    print(f"  Hybrid mode: {recommendation.get('hybrid_mode', 'auto')}")
    print(f"  Selection confidence: {recommendation['confidence']}")
    for reason in recommendation.get("selection_reasons", []):
        print(f"  Reason: {reason}")
    print(f"  Saved profile: {scan.get('profile_path', Path(default_data_dir()) / 'device_profile.json')}")
    print("=" * width)


def configure_persona_menu(data_dir: Path) -> dict:
    """Configure the persistent AI identity without starting the full model stack."""
    config = load_persona(data_dir)
    print("\nAI Name & Human Conversation / Όνομα AI και Φυσική Συζήτηση")
    print("-" * 72)
    print(describe_persona(config, "en"))
    try:
        entered_name = input(f"\nAI name [{config.get('assistant_name', 'Pocket AI')}]: ").strip()
        if entered_name:
            config["assistant_name"] = sanitize_name(entered_name)
        entered_user = input(f"Your name (optional) [{config.get('user_name', '')}]: ").strip()
        if entered_user:
            config["user_name"] = sanitize_name(entered_user, fallback="", maximum=36)
        print("\nConversation style:")
        style_names = list(PERSONA_STYLES)
        for index, style_name in enumerate(style_names, 1):
            style = PERSONA_STYLES[style_name]
            print(f"  {index}. {style.get('label_en', style_name)} / {style.get('label_el', style_name)}")
        style_choice = input(f"Select style [current: {config.get('style', 'friendly')}]: ").strip()
        if style_choice:
            if style_choice.isdigit() and 1 <= int(style_choice) <= len(style_names):
                config["style"] = style_names[int(style_choice) - 1]
            elif style_choice.casefold() in PERSONA_STYLES:
                config["style"] = style_choice.casefold()
        human_choice = input("Enable human-like natural wording? [Y/n]: ").strip().casefold()
        if human_choice in {"n", "no", "ο", "οχι", "όχι"}:
            config["human_style"] = False
        elif human_choice:
            config["human_style"] = True
        config = save_persona(data_dir, config)
        print("\nSaved / Αποθηκεύτηκε")
        print(describe_persona(config, "en"))
        return config
    except (EOFError, KeyboardInterrupt):
        print("\nConfiguration cancelled.")
        return config


def automatic_startup_scan(data_dir: Path, *, quiet: bool = False) -> dict:
    """Refresh RAM/storage and reuse a saved CPU benchmark when possible."""
    saved = load_device_profile(data_dir)
    if saved is None:
        if not quiet:
            print("Checking this phone and selecting the safest AI model...")
        return scan_phone_hardware(data_dir, save=True, run_benchmark=True)

    refreshed = scan_phone_hardware(data_dir, save=True, run_benchmark=False)
    old_benchmark = saved.get("processor", {}).get("benchmark")
    if isinstance(old_benchmark, dict) and old_benchmark.get("score"):
        refreshed["processor"]["benchmark"] = old_benchmark
        family = {
            key: refreshed["processor"].get(key)
            for key in ("vendor", "family", "known_score", "matched_pattern")
        }
        refreshed["processor"]["score"] = _derive_cpu_score(
            family,
            old_benchmark,
            refreshed["processor"]["logical_cores"],
            refreshed["processor"]["frequency"]["maximum_khz"],
            refreshed["processor"]["is_64_bit"],
        )
        refreshed["recommendation"] = _recommend_ai_configuration(refreshed)
        atomic_write_json(data_dir / "device_profile.json", refreshed)
    return refreshed


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

                CREATE TABLE IF NOT EXISTS response_cache (
                    cache_key TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    language TEXT NOT NULL,
                    response TEXT NOT NULL,
                    route TEXT NOT NULL,
                    confidence REAL NOT NULL DEFAULT 0.0,
                    hits INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_response_cache_updated
                    ON response_cache(updated_at);
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

    @staticmethod
    def _cache_key(query: str, language: str) -> str:
        normalized = normalize_text(query)
        return hashlib.sha256((language + "|" + normalized).encode("utf-8")).hexdigest()

    @staticmethod
    def _cacheable_query(query: str) -> bool:
        normalized = normalize_text(query)
        dynamic_terms = {
            "today", "current", "latest", "now", "weather", "news", "price",
            "score", "time", "date", "σημερα", "τωρα", "καιρος", "νεα",
            "τιμη", "ωρα", "ημερομηνια",
        }
        return len(normalized) >= 4 and not any(term in normalized.split() for term in dynamic_terms)

    def get_cached_response(self, query: str, language: str) -> Optional[dict]:
        if not self._cacheable_query(query):
            return None
        key = self._cache_key(query, language)
        row = self.connection.execute(
            "SELECT response,route,confidence,hits FROM response_cache WHERE cache_key=?",
            (key,)
        ).fetchone()
        if not row:
            return None
        with self.connection:
            self.connection.execute(
                "UPDATE response_cache SET hits=hits+1 WHERE cache_key=?", (key,)
            )
        return {
            "response": str(row["response"]),
            "route": "response_cache",
            "cached_route": str(row["route"]),
            "confidence": float(row["confidence"]),
            "cache_hits": int(row["hits"]) + 1,
        }

    def cache_response(
        self,
        query: str,
        language: str,
        response: str,
        route: str,
        confidence: float,
    ) -> None:
        if not self._cacheable_query(query) or not response.strip():
            return
        key = self._cache_key(query, language)
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO response_cache(
                    cache_key,query,language,response,route,confidence,hits,updated_at
                ) VALUES(?,?,?,?,?,?,0,?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    response=excluded.response,
                    route=excluded.route,
                    confidence=excluded.confidence,
                    updated_at=excluded.updated_at
                """,
                (key, query[:MAX_INPUT_CHARS], language, response, route, float(confidence), now_iso())
            )
            self.connection.execute(
                """
                DELETE FROM response_cache WHERE cache_key NOT IN (
                    SELECT cache_key FROM response_cache
                    ORDER BY updated_at DESC LIMIT 2500
                )
                """
            )

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

    @staticmethod
    def _clean_wikipedia_query(query: str) -> str:
        # Wikipedia search does not understand web-search operators. Keep the
        # human topic while removing site:/filetype:/date filters.
        cleaned = re.sub(
            r'(?i)\b(?:site|filetype|intitle|inurl|before|after)\s*:\s*(?:"[^"]+"|\S+)',
            ' ', query
        )
        cleaned = re.sub(r'(?<!\w)-[a-zA-Zα-ωΑ-Ω0-9_]+', ' ', cleaned)
        cleaned = cleaned.replace('"', ' ')
        return SPACE_RE.sub(' ', cleaned).strip()[:220]

    def _wikipedia_search(self, query: str, limit: int) -> List[dict]:
        clean_query = self._clean_wikipedia_query(query)
        if len(clean_query) < 2:
            return []
        language = 'el' if GREEK_CHAR_RE.search(clean_query) else 'en'
        params = urllib.parse.urlencode({
            'action': 'query', 'list': 'search', 'srsearch': clean_query,
            'srlimit': str(max(1, min(limit, 8))), 'format': 'json',
            'utf8': '1', 'origin': '*'
        })
        api_url = f'https://{language}.wikipedia.org/w/api.php?' + params
        data, content_type, charset = self._request(
            api_url, WEB_SEARCH_TIMEOUT, 'application/json, text/json;q=0.9'
        )
        if content_type not in {'application/json', 'text/json', 'text/plain'}:
            return []
        try:
            payload = json.loads(data.decode(charset or 'utf-8', errors='replace'))
        except (ValueError, UnicodeError, json.JSONDecodeError):
            return []
        results: List[dict] = []
        for item in payload.get('query', {}).get('search', []):
            title = str(item.get('title', '')).strip()
            if not title:
                continue
            snippet = html.unescape(HTML_TAG_RE.sub(' ', str(item.get('snippet', ''))))
            snippet = SPACE_RE.sub(' ', snippet).strip()
            article = f'https://{language}.wikipedia.org/wiki/' + urllib.parse.quote(title.replace(' ', '_'))
            try:
                article = validate_public_url(article)
            except ValueError:
                continue
            results.append({
                'title': title[:300], 'url': article,
                'snippet': snippet[:1200], 'provider': f'Wikipedia-{language}'
            })
        return results

    def _bing_rss_search(self, query: str, limit: int) -> List[dict]:
        params = urllib.parse.urlencode({'q': query, 'format': 'rss', 'count': str(limit)})
        url = 'https://www.bing.com/search?' + params
        data, content_type, _ = self._request(
            url, WEB_SEARCH_TIMEOUT, 'application/rss+xml, application/xml, text/xml;q=0.9'
        )
        if content_type not in {'application/rss+xml', 'application/xml', 'text/xml', 'text/plain'}:
            return []
        try:
            root = ET.fromstring(data)
        except ET.ParseError:
            return []
        results: List[dict] = []
        for item in root.findall('.//item'):
            title = html.unescape((item.findtext('title') or '').strip())
            link = html.unescape((item.findtext('link') or '').strip())
            description = html.unescape(HTML_TAG_RE.sub(' ', item.findtext('description') or ''))
            description = SPACE_RE.sub(' ', description).strip()
            if not title or not link:
                continue
            try:
                safe_link = validate_public_url(link)
            except ValueError:
                continue
            results.append({
                'title': title[:300], 'url': safe_link,
                'snippet': description[:1200], 'provider': 'Bing RSS'
            })
        return results

    def search(self, query: str, limit: int = 6) -> List[dict]:
        query = validate_research_query(query)
        limit = max(1, min(WEB_MAX_RESULTS, int(limit)))
        combined: List[dict] = []
        errors: List[str] = []
        for provider in (self._bing_rss_search, self._wikipedia_search):
            try:
                combined.extend(provider(query, limit))
            except (OSError, ValueError, TimeoutError, urllib.error.URLError) as error:
                errors.append(str(error))
        # Interleave providers so Wikipedia remains available even when Bing
        # returns a full page of results. This gives school/reference queries a
        # stable no-key source while retaining operator-aware web results.
        bing_items = [item for item in combined if item.get('provider') == 'Bing RSS']
        wiki_items = [item for item in combined if str(item.get('provider', '')).startswith('Wikipedia-')]
        ordered: List[dict] = []
        while bing_items or wiki_items:
            if bing_items:
                ordered.append(bing_items.pop(0))
            if wiki_items:
                ordered.append(wiki_items.pop(0))
        seen: set = set()
        results: List[dict] = []
        for item in ordered:
            url = str(item.get('url', ''))
            if not url or url in seen:
                continue
            seen.add(url)
            results.append(item)
            if len(results) >= limit:
                break
        if not results and errors:
            raise ValueError('No-key search providers were unavailable: ' + '; '.join(errors[:2]))
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
        "school_math": "PocketAI_SchoolMath_Specialist.json.gz",
        "school_science": "PocketAI_SchoolScience_Specialist.json.gz",
        "school_language": "PocketAI_SchoolLanguage_Specialist.json.gz",
        "school_humanities": "PocketAI_SchoolHumanities_Specialist.json.gz",
        "school_computing": "PocketAI_SchoolComputing_Specialist.json.gz",
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
        self.cache_model_dir = self.data_dir / GGUF_CACHE_DIRNAME
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
            "q2": "fast", "q2_k": "fast", "low": "fast", "tiny": "fast",
            "ram": "fast", "speed": "fast", "1": "fast",
            "q4": "quality", "q4_1": "quality", "small": "quality", "2": "quality",
            "qwen": "smart", "qwen0.5b": "smart", "qwen-0.5b": "smart", "recommended": "smart", "3": "smart",
            "qwen1.5b": "ultra", "qwen-1.5b": "ultra", "ultra-smart": "ultra",
            "best": "ultra", "smartest": "ultra", "strongest": "ultra", "4": "ultra",
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

    def runtime_settings(self, model_name: Optional[str] = None) -> dict:
        """Create a live plan from RAM, CPU, storage, heat, battery, and selected quantization."""
        available = available_memory_bytes()
        total = total_memory_bytes()
        selected_model = self._normalize_model_name(model_name) if model_name else self.active_model
        thermal = _thermal_snapshot()
        battery = _battery_snapshot()
        temperature = float(thermal.get("maximum_celsius", 0.0) or 0.0)
        status = str(battery.get("status", "")).casefold()
        charging = status in {"charging", "full"}
        battery_percent = int(battery.get("capacity_percent", 100) or 100)
        storage_free = int(_storage_snapshot(self.data_dir).get("free", 0) or 0)
        if optimize_phone_runtime is not None:
            plan = optimize_phone_runtime(
                model=selected_model, total_ram=total, available_ram=available,
                cpu_score=int(self.device_info.get("processor_score", 30) or 30),
                cores=max(1, int(self.device_info.get("cpu_count", os.cpu_count() or 1) or 1)),
                is_64_bit=bool(self.device_info.get("is_64_bit", sys.maxsize > 2 ** 32)),
                temperature=temperature, storage_free=storage_free,
                battery_percent=battery_percent, charging=charging, requested=self.requested_cpu_profile,
            )
            # Respect the hard per-model ceilings bundled with this package.
            plan["context"] = min(int(plan["context"]), int(EXTERNAL_LLM_MODELS[selected_model]["context"]))
            plan["max_tokens"] = min(int(plan["max_tokens"]), int(EXTERNAL_LLM_MODELS[selected_model]["max_tokens"]))
            plan.update({"available_ram": available, "total_ram": total, "temperature_celsius": temperature, "thermal_state": thermal.get("state", "unknown"), "storage_free": storage_free})
            return plan

        selected = self.resolved_cpu_profile
        profile = LLM_CPU_PROFILES[selected]
        return {
            "requested": self.requested_cpu_profile, "model": selected_model, "resolved": selected,
            "combination_id": "legacy_fallback", "threads": max(1, min(int(profile["threads"]), os.cpu_count() or 1)),
            "context": min(int(EXTERNAL_LLM_MODELS[selected_model]["context"]), int(profile["context"][selected_model])),
            "batch": int(profile["batch"]), "ubatch": int(profile["ubatch"]),
            "max_tokens": min(int(EXTERNAL_LLM_MODELS[selected_model]["max_tokens"]), int(profile["max_tokens"][selected_model])),
            "timeout": int(profile["timeout"]), "temperature": 0.22, "top_p": 0.90, "repeat_penalty": 1.12,
            "description": str(profile["description"]), "available_ram": available, "total_ram": total,
            "temperature_celsius": temperature, "thermal_state": thermal.get("state", "unknown"), "guards": [],
        }

    def set_cpu_profile(self, name: str) -> str:
        self.requested_cpu_profile = self._normalize_cpu_profile(name)
        self.device_info = self._detect_device_info()
        self.resolved_cpu_profile = self._resolve_cpu_profile()
        return self.requested_cpu_profile

    def _candidate_paths(self, filename: str) -> List[Path]:
        return [
            self.script_dir / "Models" / filename,
            self.cache_model_dir / filename,
            Path.home() / filename,
        ]

    def _split_source_available(self, filename: str, expected_sha256: str) -> bool:
        if not expected_sha256:
            return False
        status = _split_gguf_status(self.script_dir, filename, expected_sha256, verify_hashes=False)
        return bool(status.get("complete") and status.get("header_valid"))

    def _find_models(self) -> Dict[str, Path]:
        found: Dict[str, Path] = {}
        for key, config in EXTERNAL_LLM_MODELS.items():
            filename = str(config["filename"])
            for candidate in self._candidate_paths(filename):
                try:
                    if candidate.is_file() and candidate.stat().st_size > 50 * 1024 * 1024 and _gguf_header_valid(candidate):
                        found[key] = candidate
                        break
                except OSError:
                    continue
            if key not in found and self._split_source_available(filename, str(config["sha256"])):
                found[key] = self.cache_model_dir / filename
        return found

    def _ensure_model_path(self, model_key: str) -> Path:
        config = EXTERNAL_LLM_MODELS[model_key]
        filename = str(config["filename"])
        current = self.model_paths.get(model_key)
        cache_target = self.cache_model_dir / filename
        if current is not None and current.is_file() and current != cache_target:
            try:
                if current.stat().st_size > 50 * 1024 * 1024 and _gguf_header_valid(current):
                    return current
            except OSError:
                pass
        expected_sha256 = str(config.get("sha256") or "")
        if not expected_sha256:
            raise FileNotFoundError(
                f"Optional model {filename} is not installed. Use Other Files/install_smart_models.sh."
            )
        materialized = _materialize_split_gguf(
            self.script_dir,
            self.data_dir,
            filename,
            expected_sha256,
        )
        self.model_paths[model_key] = materialized
        return materialized

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
            for preferred in ("ultra", "smart", "quality", "fast"):
                if preferred in self.model_paths:
                    self.active_model = preferred
                    break
            else:
                self.active_model = next(iter(self.model_paths))

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
            materialized = bool(model_path and model_path.is_file())
            expected_digest = str(config.get("sha256") or "")
            split_status = (
                _split_gguf_status(self.script_dir, str(config["filename"]), expected_digest, verify_hashes=False)
                if expected_digest else {}
            )
            size = model_path.stat().st_size if materialized else int(split_status.get("size", 0) or 0)
            digest = ""
            sidecar_digest = ""
            if materialized:
                try:
                    digest = sha256_file(model_path)
                    sidecar = model_path.with_name(model_path.name + ".sha256")
                    if sidecar.is_file():
                        sidecar_digest = sidecar.read_text(encoding="utf-8", errors="replace").strip().split()[0]
                except (OSError, IndexError):
                    digest = ""
                    sidecar_digest = ""
            verified = bool(digest) and (digest == expected_digest if expected_digest else digest == sidecar_digest)
            models[key] = {
                "label": config["label"],
                "path": str(model_path) if model_path else "missing",
                "size": size,
                "sha256": digest or expected_digest or sidecar_digest,
                "verified": verified,
                "verification": str(config.get("verification") or "pinned SHA-256"),
                "split_package": bool(split_status.get("complete")),
                "part_count": int(split_status.get("part_count", 0) or 0),
                "materialized": materialized,
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
        if "</think>" in output:
            output = output.rsplit("</think>", 1)[-1]
        elif "<think>" in output:
            # A timeout that contains only private reasoning is not a usable answer.
            output = ""
        output = re.sub(r"<think>.*?</think>", "", output, flags=re.S | re.I)
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
        return smart_clean_answer(cleaned)[:3600]

    def generate(
        self,
        user_text: str,
        language: str,
        context: str = "",
        max_tokens: int = 192,
        specialist_instruction: str = "",
        model_name: Optional[str] = None,
        time_budget_seconds: Optional[float] = None,
        task_profile: Optional[dict] = None,
    ) -> str:
        """Run one bounded llama.cpp pass and preserve useful partial output.

        The deadline covers all compatibility attempts together, preventing an
        unsupported command-line flag from accidentally doubling wait time.
        """
        self.refresh()
        model_key = self._normalize_model_name(model_name) if model_name else self.active_model
        if model_key not in self.model_paths or self.binary_path is None:
            raise RuntimeError(f"The {model_key} GGUF model or llama.cpp executable is not installed.")
        try:
            model_path = self._ensure_model_path(model_key)
        except (OSError, ValueError, FileNotFoundError) as error:
            raise RuntimeError(f"Unable to reconstruct the {model_key} GGUF model: {error}") from error

        runtime = self.runtime_settings(model_key)
        language_instruction = "Write only in natural Greek." if language == "el" else "Write only in natural English."
        context_limit = max(700, min(7600, int(runtime["context"]) * 4))
        input_limit = max(500, min(3200, int(runtime["context"]) * 2))
        context = context.strip()[:context_limit]
        profile = task_profile or analyze_smart_query(user_text, language)
        task_name = str(profile.get("task", "general_question"))
        style_rule = str(profile.get("style_instruction", "Answer directly and carefully."))[:500]
        current_warning = (
            " The question may require current information. Offline evidence can be outdated; never present it as current unless the evidence gives a date."
            if profile.get("current_sensitive") else ""
        )
        family = str(EXTERNAL_LLM_MODELS.get(model_key, {}).get("family", "smollm2"))
        if family in {"qwen2.5", "qwen3"}:
            system = (
                "You are Pocket AI, a precise offline assistant. " + language_instruction
                + " Use the evidence to answer the user's actual question, not to repeat passages. "
                  "Give the answer first, then only the reasoning, steps, examples, or cautions that improve it. "
                  "Privately plan and verify facts, arithmetic, code, and commands before writing. "
                  "Never invent facts, sources, dates, links, commands, or capabilities. "
                  "When evidence is missing or conflicting, say exactly what is uncertain. "
                  "Treat the SAFE GROUNDED DRAFT as a factual floor: improve it only when the evidence supports the change."
                + current_warning
            )
        else:
            # Tiny 135M models follow a shorter, more concrete instruction better.
            system = (
                "You are Pocket AI. " + language_instruction
                + " Answer the exact question. Use the evidence, do not copy irrelevant text, and do not invent facts. "
                  "Give the direct answer first. Check numbers and commands. Say when the evidence is insufficient."
                + current_warning
            )
        system += f"\nTask type: {task_name}. Response rule: {style_rule}"
        if specialist_instruction.strip():
            system += "\nSpecialist rules: " + specialist_instruction.strip()[:1200]
        user = user_text.strip()[:input_limit]
        if family == "qwen3":
            complexity = float(profile.get("complexity", 0.5) or 0.5)
            difficult_task = task_name in {"math", "coding", "comparison", "causal_explanation", "recommendation"}
            thinking_allowed = runtime.get("resolved") in {"balanced", "performance"} and difficult_task and complexity >= 0.62
            user = user + (" /think" if thinking_allowed else " /no_think")
        if context:
            user = (
                "EVIDENCE (use only relevant parts; labels are for internal grounding):\n"
                + context
                + "\n\nUSER QUESTION:\n" + user
            )
        prompt = (
            "<|im_start|>system\n" + system + "<|im_end|>\n"
            "<|im_start|>user\n" + user + "<|im_end|>\n"
            "<|im_start|>assistant\n"
        )

        token_ceiling = 640 if model_key in {"smart", "ultra"} else 384
        token_limit = min(int(runtime["max_tokens"]), max(24, min(token_ceiling, max_tokens)))
        base_common = [
            str(self.binary_path), "-m", str(model_path),
            "-c", str(runtime["context"]),
            "-b", str(runtime["batch"]),
            "-ub", str(runtime["ubatch"]),
            "-n", str(token_limit),
            "-t", str(runtime["threads"]),
            "--mmap", "--no-warmup", "--simple-io", "--no-conversation",
            "--temp", f"{float(runtime.get('temperature', 0.16)):.2f}",
            "--top-p", f"{float(runtime.get('top_p', 0.86)):.2f}",
            "--repeat-penalty", f"{float(runtime.get('repeat_penalty', 1.13)):.2f}",
        ]
        qwen3_sampling = ["--top-k", "20", "--min-p", "0.0", "--presence-penalty", "1.5"] if family == "qwen3" else []
        full_common = base_common + qwen3_sampling + ["-p", prompt]
        compatible_common = base_common + ["-p", prompt]
        attempts = [
            full_common[:1] + ["--no-display-prompt"] + full_common[1:],
            full_common,
        ]
        if qwen3_sampling:
            attempts.extend([
                compatible_common[:1] + ["--no-display-prompt"] + compatible_common[1:],
                compatible_common,
            ])
        requested_budget = float(time_budget_seconds if time_budget_seconds is not None else runtime["timeout"])
        total_budget = max(5.0, min(MAX_LLM_CALL_SECONDS, float(runtime["timeout"]), requested_budget))
        deadline = time.monotonic() + total_budget
        last_error = ""
        environment = os.environ.copy()
        environment["OMP_NUM_THREADS"] = str(runtime["threads"])
        environment["OPENBLAS_NUM_THREADS"] = "1"
        environment["MKL_NUM_THREADS"] = "1"

        def timeout_text(error: subprocess.TimeoutExpired) -> str:
            chunks: List[str] = []
            seen_chunks: set[str] = set()
            for value in (getattr(error, "stdout", None), getattr(error, "output", None), getattr(error, "stderr", None)):
                if not value:
                    continue
                decoded = value.decode("utf-8", errors="replace") if isinstance(value, bytes) else str(value)
                if decoded and decoded not in seen_chunks:
                    seen_chunks.add(decoded)
                    chunks.append(decoded)
            return "\n".join(chunks)

        for command in attempts:
            remaining = deadline - time.monotonic()
            if remaining < 2.0:
                break
            try:
                completed = subprocess.run(
                    command,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    errors="replace",
                    timeout=remaining,
                    check=False,
                    env=environment,
                )
            except subprocess.TimeoutExpired as error:
                partial = self._clean_output(timeout_text(error), prompt)
                if len(partial) >= 20 and detect_language(partial) != "unsupported":
                    return partial
                last_error = f"Local inference reached its {total_budget:.0f}-second safety deadline."
                break
            except (OSError, subprocess.SubprocessError) as error:
                last_error = str(error)
                continue
            output = self._clean_output(completed.stdout, prompt)
            if completed.returncode == 0 and output:
                if detect_language(output) == "unsupported":
                    raise RuntimeError("The local model produced text outside English and Greek.")
                return output
            last_error = output or self._clean_output(completed.stderr, prompt) or f"llama.cpp returned code {completed.returncode}"
        raise RuntimeError(last_error or "Local model inference failed within the answer deadline.")


# ---------------------------------------------------------------------------
# Assistant engine
# ---------------------------------------------------------------------------



COMMON_DEFINITIONS: Dict[str, Dict[str, str]] = {
    "apple": {
        "en": "An apple is an edible fruit produced by an apple tree. It is commonly eaten fresh and contains fiber, water, vitamins, and natural sugars.",
        "el": "Το μήλο είναι ένας βρώσιμος καρπός της μηλιάς. Τρώγεται συχνά φρέσκο και περιέχει φυτικές ίνες, νερό, βιταμίνες και φυσικά σάκχαρα.",
    },
    "banana": {
        "en": "A banana is a soft, usually yellow fruit that grows in tropical regions and provides carbohydrates, fiber, and potassium.",
        "el": "Η μπανάνα είναι ένας μαλακός, συνήθως κίτρινος καρπός που αναπτύσσεται σε τροπικές περιοχές και παρέχει υδατάνθρακες, φυτικές ίνες και κάλιο.",
    },
    "fruit": {
        "en": "A fruit is the seed-bearing part of a flowering plant. In everyday food use, fruits are often sweet or tart and eaten fresh or cooked.",
        "el": "Ο καρπός είναι το μέρος ενός ανθοφόρου φυτού που περιέχει σπόρους. Στην καθημερινή διατροφή τα φρούτα είναι συχνά γλυκά ή όξινα και τρώγονται φρέσκα ή μαγειρεμένα.",
    },
    "computer": {
        "en": "A computer is an electronic device that processes data by following stored instructions called programs.",
        "el": "Ο υπολογιστής είναι μια ηλεκτρονική συσκευή που επεξεργάζεται δεδομένα ακολουθώντας αποθηκευμένες οδηγίες που ονομάζονται προγράμματα.",
    },
    "internet": {
        "en": "The internet is a worldwide network of connected computer networks that exchange data using standard communication protocols.",
        "el": "Το διαδίκτυο είναι ένα παγκόσμιο δίκτυο συνδεδεμένων δικτύων υπολογιστών που ανταλλάσσουν δεδομένα με κοινά πρωτόκολλα επικοινωνίας.",
    },
    "artificial intelligence": {
        "en": "Artificial intelligence is a field of computing that builds systems able to perform tasks associated with human intelligence, such as recognizing patterns, understanding language, or making predictions.",
        "el": "Η τεχνητή νοημοσύνη είναι κλάδος της πληροφορικής που δημιουργεί συστήματα ικανά να εκτελούν εργασίες που συνδέονται με την ανθρώπινη νοημοσύνη, όπως αναγνώριση προτύπων, κατανόηση γλώσσας και προβλέψεις.",
    },
    "machine learning": {
        "en": "Machine learning is a part of artificial intelligence in which a model learns patterns from examples instead of receiving a separate hand-written rule for every situation.",
        "el": "Η μηχανική μάθηση είναι μέρος της τεχνητής νοημοσύνης όπου ένα μοντέλο μαθαίνει πρότυπα από παραδείγματα αντί να λαμβάνει έναν ξεχωριστό χειρόγραφο κανόνα για κάθε περίπτωση.",
    },
    "neural network": {
        "en": "A neural network is a machine-learning model made of connected mathematical units arranged in layers. Training adjusts their numerical weights so the network can recognize patterns or make predictions.",
        "el": "Ένα νευρωνικό δίκτυο είναι μοντέλο μηχανικής μάθησης από συνδεδεμένες μαθηματικές μονάδες σε επίπεδα. Η εκπαίδευση προσαρμόζει τα αριθμητικά βάρη τους ώστε να αναγνωρίζει πρότυπα ή να κάνει προβλέψεις.",
    },
    "python": {
        "en": "Python is a general-purpose programming language known for readable syntax and a large ecosystem of libraries.",
        "el": "Η Python είναι μια γλώσσα προγραμματισμού γενικού σκοπού, γνωστή για την ευανάγνωστη σύνταξη και το μεγάλο οικοσύστημα βιβλιοθηκών της.",
    },
    "termux": {
        "en": "Termux is an Android terminal application that provides a Linux-like command-line environment without requiring root.",
        "el": "Το Termux είναι εφαρμογή τερματικού για Android που παρέχει περιβάλλον γραμμής εντολών παρόμοιο με Linux χωρίς να απαιτεί root.",
    },
    "ram": {
        "en": "RAM is fast temporary memory used by running applications. Its contents are normally lost when the device is powered off.",
        "el": "Η RAM είναι γρήγορη προσωρινή μνήμη που χρησιμοποιείται από εφαρμογές που εκτελούνται. Τα περιεχόμενά της συνήθως χάνονται όταν απενεργοποιηθεί η συσκευή.",
    },
    "storage": {
        "en": "Storage is persistent space used to keep applications, documents, photos, models, and other files even after the device is turned off.",
        "el": "Ο αποθηκευτικός χώρος είναι μόνιμος χώρος για εφαρμογές, έγγραφα, φωτογραφίες, μοντέλα και άλλα αρχεία ακόμη και μετά την απενεργοποίηση της συσκευής.",
    },
    "cpu": {
        "en": "A CPU, or central processing unit, executes program instructions and coordinates much of a device's computation.",
        "el": "Η CPU, ή κεντρική μονάδα επεξεργασίας, εκτελεί τις εντολές των προγραμμάτων και συντονίζει μεγάλο μέρος των υπολογισμών μιας συσκευής.",
    },
    "ai model": {
        "en": "An AI model is a trained mathematical system that transforms input data into predictions, classifications, generated text, or other outputs.",
        "el": "Ένα μοντέλο AI είναι ένα εκπαιδευμένο μαθηματικό σύστημα που μετατρέπει δεδομένα εισόδου σε προβλέψεις, κατηγορίες, παραγόμενο κείμενο ή άλλα αποτελέσματα.",
    },
    "water": {
        "en": "Water is a chemical compound made of two hydrogen atoms and one oxygen atom, written H₂O. It is essential for known life.",
        "el": "Το νερό είναι χημική ένωση από δύο άτομα υδρογόνου και ένα άτομο οξυγόνου, με τύπο H₂O. Είναι απαραίτητο για τη γνωστή ζωή.",
    },
    "gravity": {
        "en": "Gravity is the attraction between objects with mass. Near Earth, it pulls objects toward the planet's center.",
        "el": "Η βαρύτητα είναι η έλξη μεταξύ αντικειμένων που έχουν μάζα. Κοντά στη Γη τραβά τα αντικείμενα προς το κέντρο του πλανήτη.",
    },
    "earth": {
        "en": "Earth is the third planet from the Sun and the only world currently known to support life.",
        "el": "Η Γη είναι ο τρίτος πλανήτης από τον Ήλιο και ο μόνος κόσμος που γνωρίζουμε σήμερα ότι υποστηρίζει ζωή.",
    },
    "sun": {
        "en": "The Sun is the star at the center of our Solar System. Its light and heat are powered mainly by nuclear fusion in its core.",
        "el": "Ο Ήλιος είναι το άστρο στο κέντρο του Ηλιακού Συστήματος. Το φως και η θερμότητά του παράγονται κυρίως από πυρηνική σύντηξη στον πυρήνα του.",
    },
    "moon": {
        "en": "The Moon is Earth's natural satellite. It orbits Earth and strongly influences ocean tides.",
        "el": "Η Σελήνη είναι ο φυσικός δορυφόρος της Γης. Περιφέρεται γύρω από τη Γη και επηρεάζει σημαντικά τις παλίρροιες.",
    },
    "atom": {
        "en": "An atom is the smallest unit of an element that retains that element's chemical properties. It contains a nucleus surrounded by electrons.",
        "el": "Το άτομο είναι η μικρότερη μονάδα ενός στοιχείου που διατηρεί τις χημικές ιδιότητές του. Περιέχει πυρήνα που περιβάλλεται από ηλεκτρόνια.",
    },
    "dna": {
        "en": "DNA is the molecule that stores hereditary biological information in most living organisms.",
        "el": "Το DNA είναι το μόριο που αποθηκεύει τις κληρονομικές βιολογικές πληροφορίες στους περισσότερους ζωντανούς οργανισμούς.",
    },
    "electricity": {
        "en": "Electricity describes phenomena caused by electric charge, including the movement of electrons through a conductor.",
        "el": "Ο ηλεκτρισμός περιγράφει φαινόμενα που προκαλούνται από ηλεκτρικό φορτίο, όπως η κίνηση ηλεκτρονίων μέσα από έναν αγωγό.",
    },
    "photosynthesis": {
        "en": "Photosynthesis is the process by which plants, algae, and some microorganisms use light energy to produce chemical energy, usually from carbon dioxide and water.",
        "el": "Η φωτοσύνθεση είναι η διαδικασία με την οποία φυτά, φύκη και ορισμένοι μικροοργανισμοί χρησιμοποιούν φωτεινή ενέργεια για να παράγουν χημική ενέργεια, συνήθως από διοξείδιο του άνθρακα και νερό.",
    },
    "greece": {
        "en": "Greece is a country in southeastern Europe with its capital in Athens. It includes a mountainous mainland and many islands.",
        "el": "Η Ελλάδα είναι χώρα της νοτιοανατολικής Ευρώπης με πρωτεύουσα την Αθήνα. Περιλαμβάνει ορεινή ηπειρωτική χώρα και πολλά νησιά.",
    },
}

COMMON_DEFINITION_ALIASES = {
    "apple": "apple", "an apple": "apple", "μηλο": "apple", "μηλο καρποσ": "apple",
    "banana": "banana", "a banana": "banana", "μπανανα": "banana",
    "fruit": "fruit", "a fruit": "fruit", "φρουτο": "fruit", "καρποσ": "fruit",
    "computer": "computer", "a computer": "computer", "υπολογιστησ": "computer",
    "internet": "internet", "the internet": "internet", "διαδικτυο": "internet", "ιντερνετ": "internet",
    "artificial intelligence": "artificial intelligence", "ai": "artificial intelligence", "τεχνητη νοημοσυνη": "artificial intelligence",
    "machine learning": "machine learning", "μηχανικη μαθηση": "machine learning",
    "neural network": "neural network", "νευρωνικο δικτυο": "neural network",
    "python": "python", "termux": "termux", "ram": "ram", "memory": "ram", "μνημη ram": "ram",
    "storage": "storage", "phone storage": "storage", "αποθηκευτικοσ χωροσ": "storage",
    "cpu": "cpu", "processor": "cpu", "επεξεργαστησ": "cpu",
    "ai model": "ai model", "model": "ai model", "μοντελο ai": "ai model",
    "water": "water", "νερο": "water", "gravity": "gravity", "βαρυτητα": "gravity",
    "earth": "earth", "γη": "earth", "sun": "sun", "ηλιοσ": "sun", "moon": "moon", "σεληνη": "moon", "φεγγαρι": "moon",
    "atom": "atom", "ατομο": "atom", "dna": "dna", "electricity": "electricity", "ηλεκτρισμοσ": "electricity",
    "photosynthesis": "photosynthesis", "φωτοσυνθεση": "photosynthesis", "greece": "greece", "ελλαδα": "greece",
}


COMMON_COMPARISONS: List[dict] = [
    {
        "left": ("tcp", "transmission control protocol"),
        "right": ("udp", "user datagram protocol"),
        "en": (
            "TCP and UDP both carry application data over IP, but they optimize for different goals. "
            "TCP creates a connection, preserves order, detects loss, retransmits missing data, and applies flow and congestion control; this makes it reliable but adds overhead and delay. "
            "UDP sends independent datagrams without guaranteeing delivery or order; it has less overhead and is useful when fresh data matters more than perfect delivery. "
            "Use TCP for web pages, logins, email, and file transfer. Use UDP for many real-time calls, live media, games, DNS, or applications that implement their own recovery. "
            "Neither protocol provides encryption by itself."
        ),
        "el": (
            "Τα TCP και UDP μεταφέρουν δεδομένα εφαρμογών πάνω από IP, αλλά εξυπηρετούν διαφορετικούς στόχους. "
            "Το TCP δημιουργεί σύνδεση, διατηρεί τη σειρά, εντοπίζει απώλειες, επαναμεταδίδει δεδομένα και εφαρμόζει έλεγχο ροής και συμφόρησης· έτσι είναι αξιόπιστο αλλά έχει μεγαλύτερο κόστος και καθυστέρηση. "
            "Το UDP στέλνει ανεξάρτητα datagrams χωρίς εγγύηση παράδοσης ή σειράς· έχει μικρότερο κόστος και ταιριάζει όταν τα φρέσκα δεδομένα είναι σημαντικότερα από την τέλεια παράδοση. "
            "Χρησιμοποίησε TCP για ιστοσελίδες, συνδέσεις, email και αρχεία, και UDP για πολλές κλήσεις πραγματικού χρόνου, live media, παιχνίδια, DNS ή εφαρμογές με δικό τους μηχανισμό ανάκτησης. "
            "Κανένα από τα δύο δεν παρέχει μόνο του κρυπτογράφηση."
        ),
    },
    {
        "left": ("http",), "right": ("https",),
        "en": "HTTP transfers web requests and responses without transport encryption. HTTPS is HTTP protected by TLS, which encrypts traffic, authenticates the server certificate, and detects tampering. Use HTTPS for essentially every modern website; it protects data in transit but does not prove that the website itself is honest or malware-free.",
        "el": "Το HTTP μεταφέρει αιτήματα και απαντήσεις web χωρίς κρυπτογράφηση μεταφοράς. Το HTTPS είναι HTTP προστατευμένο με TLS, το οποίο κρυπτογραφεί την κίνηση, πιστοποιεί τον διακομιστή και εντοπίζει αλλοίωση. Χρησιμοποίησε HTTPS σχεδόν για κάθε σύγχρονο ιστότοπο· προστατεύει τα δεδομένα κατά τη μεταφορά, αλλά δεν αποδεικνύει ότι ο ιστότοπος είναι έντιμος ή ασφαλής από κακόβουλο λογισμικό.",
    },
    {
        "left": ("ram", "memory", "μνημη ram"), "right": ("storage", "disk", "αποθηκευση", "αποθηκευτικος χωρος"),
        "en": "RAM is fast working memory used by running programs and is normally cleared when power is lost. Storage keeps apps and files persistently and is much larger but slower. More RAM improves multitasking and lets larger AI models run; more storage lets you keep more models and data but does not directly make inference faster.",
        "el": "Η RAM είναι γρήγορη μνήμη εργασίας για προγράμματα που εκτελούνται και συνήθως αδειάζει όταν χαθεί η τροφοδοσία. Η αποθήκευση κρατά μόνιμα εφαρμογές και αρχεία, είναι πολύ μεγαλύτερη αλλά πιο αργή. Περισσότερη RAM βοηθά το multitasking και επιτρέπει μεγαλύτερα μοντέλα AI· περισσότερος αποθηκευτικός χώρος επιτρέπει περισσότερα μοντέλα και δεδομένα, αλλά δεν κάνει από μόνος του την παραγωγή απαντήσεων γρηγορότερη.",
    },
    {
        "left": ("cpu", "processor", "επεξεργαστης"), "right": ("gpu", "graphics processor", "καρτα γραφικων"),
        "en": "A CPU has a small number of flexible cores optimized for general-purpose work, operating-system tasks, and low-latency control flow. A GPU has many simpler parallel units optimized for repeating similar numerical operations over large data sets. CPUs are broadly capable; GPUs can accelerate graphics and many AI workloads when the software supports them.",
        "el": "Η CPU έχει λίγους ευέλικτους πυρήνες για εργασίες γενικού σκοπού, λειτουργικό σύστημα και ροές ελέγχου χαμηλής καθυστέρησης. Η GPU έχει πολλές απλούστερες παράλληλες μονάδες για επαναλαμβανόμενους αριθμητικούς υπολογισμούς σε μεγάλα σύνολα δεδομένων. Η CPU είναι γενικής χρήσης, ενώ η GPU μπορεί να επιταχύνει γραφικά και πολλές εργασίες AI όταν το λογισμικό την υποστηρίζει.",
    },
    {
        "left": ("encryption", "κρυπτογραφηση"), "right": ("hashing", "hash", "κατακερματισμος"),
        "en": "Encryption is reversible with the correct key and is used to keep data confidential. Hashing is designed to be one-way and produces a fixed-size digest used for integrity checks, indexing, and password verification with a suitable salted password-hashing algorithm. A plain fast hash is not encryption and should not be used alone to store passwords.",
        "el": "Η κρυπτογράφηση είναι αναστρέψιμη με το σωστό κλειδί και χρησιμοποιείται για εμπιστευτικότητα. Ο κατακερματισμός είναι σχεδιασμένος ως μονόδρομη διαδικασία και παράγει σύνοψη σταθερού μεγέθους για έλεγχο ακεραιότητας, ευρετηρίαση και επαλήθευση κωδικών με κατάλληλο salted password-hashing αλγόριθμο. Ένα απλό γρήγορο hash δεν είναι κρυπτογράφηση και δεν πρέπει να χρησιμοποιείται μόνο του για αποθήκευση κωδικών.",
    },
    {
        "left": ("symmetric encryption", "συμμετρικη κρυπτογραφηση"), "right": ("asymmetric encryption", "ασυμμετρη κρυπτογραφηση"),
        "en": "Symmetric encryption uses the same secret key to encrypt and decrypt; it is fast and suited to bulk data, but the key must be shared securely. Asymmetric encryption uses a public/private key pair; it simplifies authentication and key exchange but is slower. Real protocols such as TLS usually combine them: asymmetric methods establish trust and a session key, then symmetric encryption protects the data.",
        "el": "Η συμμετρική κρυπτογράφηση χρησιμοποιεί το ίδιο μυστικό κλειδί για κρυπτογράφηση και αποκρυπτογράφηση· είναι γρήγορη για μεγάλο όγκο δεδομένων, αλλά το κλειδί πρέπει να μοιραστεί με ασφάλεια. Η ασύμμετρη χρησιμοποιεί ζεύγος δημόσιου/ιδιωτικού κλειδιού· διευκολύνει πιστοποίηση και ανταλλαγή κλειδιών αλλά είναι πιο αργή. Πρωτόκολλα όπως το TLS τα συνδυάζουν: ασύμμετρες μέθοδοι δημιουργούν εμπιστοσύνη και session key και μετά συμμετρική κρυπτογράφηση προστατεύει τα δεδομένα.",
    },
    {
        "left": ("ipv4",), "right": ("ipv6",),
        "en": "IPv4 uses 32-bit addresses and has a limited address space, so NAT is common. IPv6 uses 128-bit addresses, provides an enormous address space, and improves autoconfiguration and end-to-end addressing. IPv6 is not automatically more secure, and both versions can coexist through dual-stack or transition mechanisms.",
        "el": "Το IPv4 χρησιμοποιεί διευθύνσεις 32 bit και έχει περιορισμένο χώρο διευθύνσεων, γι’ αυτό το NAT είναι συνηθισμένο. Το IPv6 χρησιμοποιεί 128 bit, προσφέρει τεράστιο χώρο διευθύνσεων και καλύτερη αυτόματη ρύθμιση και end-to-end διευθυνσιοδότηση. Το IPv6 δεν είναι αυτόματα ασφαλέστερο και οι δύο εκδόσεις μπορούν να συνυπάρχουν με dual-stack ή μηχανισμούς μετάβασης.",
    },
]

COMMON_EXPLANATIONS: List[dict] = [
    {
        "concepts": ("photosynthesis", "φωτοσυνθεση"),
        "en": (
            "Photosynthesis converts light energy into stored chemical energy. Chlorophyll in chloroplasts absorbs light; the light-dependent reactions use that energy to split water, release oxygen, and produce energy-carrying molecules. The Calvin cycle then uses those molecules to fix carbon dioxide into sugars. A simplified overall equation is 6 CO₂ + 6 H₂O + light → C₆H₁₂O₆ + 6 O₂. Sunlight is needed because it supplies the energy that drives the first stage."
        ),
        "el": (
            "Η φωτοσύνθεση μετατρέπει τη φωτεινή ενέργεια σε αποθηκευμένη χημική ενέργεια. Η χλωροφύλλη στους χλωροπλάστες απορροφά φως· οι φωτοεξαρτώμενες αντιδράσεις χρησιμοποιούν αυτή την ενέργεια για να διασπάσουν νερό, να απελευθερώσουν οξυγόνο και να παράγουν μόρια μεταφοράς ενέργειας. Έπειτα ο κύκλος Calvin χρησιμοποιεί αυτά τα μόρια για να δεσμεύσει διοξείδιο του άνθρακα και να σχηματίσει σάκχαρα. Μια απλοποιημένη συνολική εξίσωση είναι 6 CO₂ + 6 H₂O + φως → C₆H₁₂O₆ + 6 O₂. Το ηλιακό φως χρειάζεται επειδή παρέχει την ενέργεια που κινεί το πρώτο στάδιο."
        ),
    },
    {
        "concepts": ("dns", "domain name system", "συστημα ονοματων τομεα"),
        "en": "DNS translates human-readable domain names into records such as IP addresses. A device asks a recursive resolver, which may answer from cache or query the DNS hierarchy from root servers to the relevant top-level-domain and authoritative server. DNSSEC can authenticate signed DNS data, while encrypted transports such as DoH or DoT protect the query path to the resolver; these solve different problems.",
        "el": "Το DNS μεταφράζει ονόματα τομέων σε εγγραφές όπως διευθύνσεις IP. Η συσκευή ρωτά έναν recursive resolver, ο οποίος απαντά από cache ή ακολουθεί την ιεραρχία DNS από root servers προς τον κατάλληλο TLD και authoritative server. Το DNSSEC μπορεί να πιστοποιήσει υπογεγραμμένα δεδομένα DNS, ενώ μεταφορές όπως DoH ή DoT κρυπτογραφούν τη διαδρομή του ερωτήματος προς τον resolver· λύνουν διαφορετικά προβλήματα.",
    },
    {
        "concepts": ("artificial intelligence", "ai model", "τεχνητη νοημοσυνη", "μοντελο ai"),
        "en": "An AI model learns numerical patterns from training examples. During inference it receives new input, transforms it through learned parameters, and produces probabilities or generated output. A language model predicts likely next tokens from context; larger and better-trained models usually represent more patterns, while retrieval can supply facts that are not reliably stored in the parameters.",
        "el": "Ένα μοντέλο AI μαθαίνει αριθμητικά πρότυπα από παραδείγματα εκπαίδευσης. Κατά το inference λαμβάνει νέα είσοδο, την επεξεργάζεται μέσω των μαθημένων παραμέτρων και παράγει πιθανότητες ή περιεχόμενο. Ένα γλωσσικό μοντέλο προβλέπει πιθανά επόμενα tokens από το context· μεγαλύτερα και καλύτερα εκπαιδευμένα μοντέλα συνήθως αναπαριστούν περισσότερα πρότυπα, ενώ το retrieval μπορεί να τους δώσει γεγονότα που δεν έχουν αποθηκευτεί αξιόπιστα στις παραμέτρους.",
    },
]


def _contains_phrase(normalized: str, phrase: str) -> bool:
    phrase_normalized = normalize_text(phrase)
    return bool(phrase_normalized and re.search(r"(?<![0-9a-zα-ω])" + re.escape(phrase_normalized) + r"(?![0-9a-zα-ω])", normalized))


def common_structured_response(text: str, language: str) -> Optional[Tuple[str, str]]:
    normalized = normalize_text(text)
    comparison_cues = ("compare", "comparison", "versus", " vs ", "difference", "differences", "συγκρινε", "συγκριση", "διαφορα", "διαφορες")
    if any(normalize_text(cue).strip() in normalized for cue in comparison_cues):
        for entry in COMMON_COMPARISONS:
            left = any(_contains_phrase(normalized, alias) for alias in entry["left"])
            right = any(_contains_phrase(normalized, alias) for alias in entry["right"])
            if left and right:
                return str(entry["el" if language == "el" else "en"]), "verified_comparison"

    explanation_cues = ("why", "how does", "how do", "how is", "explain", "mechanism", "γιατι", "πως λειτουργει", "εξηγησε")
    if any(normalize_text(cue) in normalized for cue in explanation_cues):
        for entry in COMMON_EXPLANATIONS:
            if any(_contains_phrase(normalized, concept) for concept in entry["concepts"]):
                return str(entry["el" if language == "el" else "en"]), "verified_explanation"
    return None


def common_definition_response(text: str, language: str) -> Optional[str]:
    normalized = normalize_text(text).strip(" ?.!,:;")
    prefixes = (
        "what is ", "what's ", "define ", "explain ", "teach me about ", "tell me what ", "tell me about ",
        "τι ειναι ", "ορισε ", "εξηγησε ", "μαθε μου για ", "πες μου τι ειναι ", "πες μου για ",
    )
    subject = None
    for prefix in prefixes:
        if normalized.startswith(prefix):
            subject = normalized[len(prefix):].strip(" ?.!,:;")
            break
    if subject is None:
        return None
    subject = re.sub(r"^(?:a|an|the|ενα|ενας|μια|το|η|ο)\s+", "", subject).strip()
    key = COMMON_DEFINITION_ALIASES.get(subject)
    if key is None:
        return None
    return COMMON_DEFINITIONS[key]["el" if language == "el" else "en"]


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
        self.persona = load_persona(self.data_dir)
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
        self.school_tutor = SchoolTutor(models_dir / "PocketAI_School_Knowledge.json.gz")
        self.universal_knowledge = UniversalKnowledge(models_dir / "PocketAI_Universal_Knowledge.json.gz")
        self.lexical_knowledge = LexicalKnowledge(models_dir / "Lexical Knowledge")
        self.encyclopedia_knowledge = EncyclopediaKnowledge(models_dir / "Encyclopedia Knowledge")
        self.conversation_engine = ConversationEngine()
        self.hybrid_components: Dict[str, dict] = {}
        for component_id, filename in HYBRID_COMPONENT_FILES.items():
            component_path = models_dir / filename
            try:
                with gzip.open(component_path, "rt", encoding="utf-8") as handle:
                    payload = json.load(handle)
                if isinstance(payload, dict):
                    self.hybrid_components[component_id] = payload
            except (OSError, ValueError, json.JSONDecodeError):
                continue
        stored_llm_model = self.store.get_setting("llm_model", DEFAULT_EXTERNAL_LLM_MODEL) or DEFAULT_EXTERNAL_LLM_MODEL
        stored_cpu_profile = self.store.get_setting("llm_cpu_profile", DEFAULT_LLM_CPU_PROFILE) or DEFAULT_LLM_CPU_PROFILE
        self.local_llm = LocalGGUFModel(
            data_dir,
            preferred_model=stored_llm_model,
            cpu_profile=stored_cpu_profile,
        )
        stored_llm_mode = self.store.get_setting("llm_mode", "always") or "always"
        self.llm_mode = stored_llm_mode if stored_llm_mode in {"off", "fallback", "always"} else "always"
        stored_hybrid_mode = self.store.get_setting("hybrid_mode", DEFAULT_HYBRID_MODE) or DEFAULT_HYBRID_MODE
        self.hybrid_mode = stored_hybrid_mode if stored_hybrid_mode in HYBRID_MODES else DEFAULT_HYBRID_MODE
        # Old cached/template answers can make an upgraded build appear unchanged.
        # Invalidate them once when the smartness pipeline changes.
        smartness_version = "9-natural-complete-school"
        if self.store.get_setting("smartness_version", "") != smartness_version:
            try:
                with self.store.connection:
                    self.store.connection.execute("DELETE FROM response_cache")
            except sqlite3.Error:
                pass
            if "smart" in self.local_llm.model_paths:
                self.local_llm.active_model = "smart"
                self.store.set_setting("llm_model", "smart")
            self.llm_mode = "always"
            self.store.set_setting("llm_mode", "always")
            self.store.set_setting("smartness_version", smartness_version)

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
        return sanitize_name(self.persona.get("assistant_name", self.dataset.get("assistant_name", APP_NAME)))

    def update_persona(self, *, assistant_name: Optional[str] = None, user_name: Optional[str] = None,
                       style: Optional[str] = None, human_style: Optional[bool] = None) -> dict:
        config = dict(self.persona)
        if assistant_name is not None:
            config["assistant_name"] = sanitize_name(assistant_name)
        if user_name is not None:
            config["user_name"] = sanitize_name(user_name, fallback="", maximum=36) if user_name else ""
        if style is not None:
            normalized = style.casefold().strip()
            if normalized not in PERSONA_STYLES:
                raise ValueError("Unknown style. Use friendly, calm_expert, casual, mentor, or direct.")
            config["style"] = normalized
        if human_style is not None:
            config["human_style"] = bool(human_style)
        self.persona = save_persona(self.data_dir, config)
        if self.persona.get("user_name"):
            try:
                self.store.set_memory("user_name", str(self.persona["user_name"]))
            except sqlite3.Error:
                pass
        return self.persona

    def persona_guidance(self, language: str) -> str:
        return persona_instruction(self.persona, language)

    def apply_persona(self, response: str, language: str, route: str, seed_text: str) -> str:
        return naturalize_response(response, language, self.persona, route=route, seed_text=seed_text)

    def close(self) -> None:
        try:
            self.school_tutor.close()
        except Exception:
            pass
        try:
            self.encyclopedia_knowledge.close()
        except Exception:
            pass
        try:
            self.lexical_knowledge.close()
        except Exception:
            pass
        try:
            self.universal_knowledge.close()
        except Exception:
            pass
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
        try:
            enriched, used = self.conversation_engine.contextualize(
                text, self.session_history, language, getattr(self.universal_knowledge, "last_topic", "")
            )
            if used:
                return enriched, True
        except Exception:
            pass
        if not self.last_user_query or not is_followup_message(text, language):
            return text, False
        previous = self.last_user_query.strip()
        if not previous or normalize_text(previous) == normalize_text(text):
            return text, False
        return previous + " " + text, True

    def format_response(self, text: str, language: Optional[str] = None) -> str:
        language = language or self.last_language
        now = _dt.datetime.now().astimezone()
        name = self.persona.get("user_name") or self.store.get_memory("name") or self.store.get_memory("user_name") or ""
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

        advanced_exact = solve_advanced_tool_query(stripped, language)
        if advanced_exact is not None:
            return str(advanced_exact.get("response", "")), str(advanced_exact.get("route", "advanced_exact_tool"))

        structured = common_structured_response(stripped, language)
        if structured is not None:
            return structured

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
        thermal = _thermal_snapshot()
        temperature = thermal.get("maximum_celsius", 0.0)
        return self.t(
            f"Python {sys.version.split()[0]}; platform {sys.platform}; RAM {human_size(available)} available of {human_size(total)}; storage {disk_en}; temperature {temperature:.1f}°C ({thermal.get('state', 'unknown')}); profile {self.profile_name}; hybrid {self.hybrid_mode}; language mode {self.language_mode}.",
            f"Python {sys.version.split()[0]}; πλατφόρμα {sys.platform}; διαθέσιμη RAM {human_size(available)} από {human_size(total)}; αποθήκευση {disk_el}; θερμοκρασία {temperature:.1f}°C ({thermal.get('state', 'unknown')}); profile {self.profile_name}; υβριδική λειτουργία {self.hybrid_mode}; λειτουργία γλώσσας {self.language_mode}.",
            language
        )

    def collect_smart_evidence(
        self,
        query: str,
        language: str,
        task_profile: dict,
        candidates: Sequence[dict] = (),
        school_answer: Optional[dict] = None,
        universal_answer: Optional[dict] = None,
        common_answer: Optional[str] = None,
        lexical_answer: Optional[dict] = None,
        encyclopedia_answer: Optional[dict] = None,
        specialist_knowledge: Optional[dict] = None,
    ) -> Tuple[str, List[dict], List[dict]]:
        """Collect and rerank all local evidence before a tiny model sees it."""
        sources: List[dict] = []
        seen: set[Tuple[str, str]] = set()

        def add_source(source_type: str, title: str, text: str, score: float = 0.65) -> None:
            clean = re.sub(r"\s+", " ", str(text)).strip()
            clean_title = re.sub(r"\s+", " ", str(title)).strip() or source_type.replace("_", " ").title()
            if not clean:
                return
            key = (normalize_text(clean_title), normalize_text(clean[:500]))
            if key in seen:
                return
            seen.add(key)
            sources.append({
                "source_type": source_type,
                "title": clean_title[:140],
                "text": clean[:2600],
                "score": max(0.0, min(1.0, float(score))),
            })

        if school_answer:
            school_title = str(school_answer.get("topic") or school_answer.get("subject") or "School foundation")
            school_text = str(school_answer.get("response", ""))
            extra_school_evidence = str(school_answer.get("school_evidence", "") or "")
            if extra_school_evidence:
                school_text = (school_text + "\n\nLocal reference evidence: " + extra_school_evidence).strip()
            add_source("school", school_title, school_text, float(school_answer.get("match_score", school_answer.get("match", 0.90)) or 0.90))
        if universal_answer:
            title = str(universal_answer.get("title") or universal_answer.get("knowledge_id") or "Curated knowledge")
            add_source("universal", title, universal_answer.get("response", ""), float(universal_answer.get("match_score", 0.88) or 0.88))
        if common_answer:
            add_source("common", "Core verified definition", common_answer, 0.97)
        if lexical_answer:
            add_source("lexical", "WordNet lexical evidence", lexical_answer.get("response", ""), float(lexical_answer.get("match_score", 0.82) or 0.82))
        if encyclopedia_answer:
            add_source("encyclopedia", str(encyclopedia_answer.get("title") or "Offline encyclopedia"), encyclopedia_answer.get("response", ""), float(encyclopedia_answer.get("match_score", 0.88) or 0.88))
        if specialist_knowledge:
            add_source("specialist", str(specialist_knowledge.get("specialist") or "Task specialist"), specialist_knowledge.get("response", ""), float(specialist_knowledge.get("match_score", 0.78) or 0.78))

        # Pull multiple passages instead of trusting one top hit.  The smart
        # reranker then selects sentences that answer the requested task type.
        try:
            for item in self.encyclopedia_knowledge.retrieve(query, limit=9):
                add_source(
                    "encyclopedia",
                    str(item.get("title") or "Offline encyclopedia"),
                    str(item.get("text") or ""),
                    float(item.get("score", 0.60) or 0.60),
                )
        except Exception:
            pass
        try:
            for item in self.lexical_knowledge.retrieve(query, language=language, limit=7):
                lemmas = item.get("greek_lemmas") if language == "el" and item.get("greek_lemmas") else item.get("english_lemmas")
                title = ", ".join(str(value) for value in (lemmas or [])[:4]) or str(item.get("id") or "WordNet concept")
                relation_bits = []
                if item.get("definition"):
                    relation_bits.append(str(item["definition"]))
                if item.get("examples"):
                    relation_bits.extend(str(value) for value in item.get("examples", [])[:2])
                add_source("lexical", title, " ".join(relation_bits), float(item.get("score", 0.58) or 0.58))
        except Exception:
            pass

        for candidate in candidates[:10]:
            source_type = "taught_qa" if candidate.get("kind") == "qa" else "local_document"
            title = str(candidate.get("source") or candidate.get("prompt") or source_type)
            add_source(source_type, title, str(candidate.get("response") or ""), float(candidate.get("score", 0.50) or 0.50))

        try:
            active = self.local_llm.active_model
            runtime = self.local_llm.runtime_settings(active)
            context_tokens = int(runtime.get("context", 768) or 768)
        except Exception:
            active, context_tokens = "quality", 768
        evidence_ceiling = 7600 if active == "ultra" else (6200 if active == "smart" else 3400)
        max_chars = min(evidence_ceiling, max(1100, int(context_tokens * 3.15)))
        packet, ranked = build_evidence_packet(
            query, sources, language=language, task_profile=task_profile, max_chars=max_chars
        )
        return packet, list(ranked), sources

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
            return response, {"route": "language_reject", "language": "unsupported"}

        task_profile = analyze_smart_query(original_text, language)
        contextual_text, context_used = self.contextualize_query(original_text, language)
        specialist = self.specialists.select(contextual_text)
        user_name = str(self.persona.get("user_name", "") or self.store.get_memory("name") or "")
        social = self.conversation_engine.social_reply(original_text, language, self.assistant_name, user_name)
        utility = None if social is not None else self.direct_utility_response(original_text, language)

        if social is not None:
            response = social
            details = {"route": "natural_conversation", "language": language, "context_used": False, "task_profile": task_profile}
        elif utility is not None:
            response, route = utility
            details = {"route": route, "language": language, "context_used": False, "task_profile": task_profile}
        else:
            response = ""
            details = {"language": language, "context_used": context_used, "task_profile": task_profile}
            candidates: List[dict] = []
            ranked_evidence: List[dict] = []
            evidence_packet = ""

            cached_answer = None
            if not task_profile.get("current_sensitive"):
                cached_answer = self.store.get_cached_response(original_text, language)
            if cached_answer is not None and float(cached_answer.get("confidence", 0.0) or 0.0) >= 0.72:
                response = str(cached_answer["response"])
                details.update(cached_answer)
            else:
                school_answer = self.school_tutor.answer(original_text, language)
                universal_answer = self.universal_knowledge.answer(original_text, language)
                common_answer = common_definition_response(original_text, language)
                try:
                    lexical_answer = self.lexical_knowledge.answer(original_text, language)
                except Exception:
                    lexical_answer = None
                try:
                    encyclopedia_answer = self.encyclopedia_knowledge.answer(original_text, language)
                except Exception:
                    encyclopedia_answer = None

                # Prevent an everyday word from being hijacked by a programming alias.
                if universal_answer is not None and lexical_answer is not None:
                    uid = str(universal_answer.get("knowledge_id", ""))
                    category = str(universal_answer.get("category", ""))
                    technical_cues = {
                        "python", "code", "function", "method", "module", "library", "api",
                        "matplotlib", "programming", "κωδικ", "συναρτηση", "βιβλιοθηκ", "προγραμματισ",
                    }
                    normalized_query = normalize_text(original_text)
                    if (uid.startswith("py_") or category.endswith("_reference")) and not any(cue in normalized_query for cue in technical_cues):
                        universal_answer = None

                candidates = self.store.retrieve_many(contextual_text, limit=8, candidate_limit=80, language=language)
                specialist_knowledge = self.specialists.knowledge_answer(
                    contextual_text, language, selected=specialist
                )
                evidence_packet, ranked_evidence, evidence_sources = self.collect_smart_evidence(
                    contextual_text, language, task_profile, candidates=candidates,
                    school_answer=school_answer, universal_answer=universal_answer,
                    common_answer=common_answer, lexical_answer=lexical_answer,
                    encyclopedia_answer=encyclopedia_answer, specialist_knowledge=specialist_knowledge,
                )
                details["evidence_count"] = len(ranked_evidence)
                details["evidence_source_count"] = len(evidence_sources)
                details["evidence_chars"] = len(evidence_packet)

                requested_depth = str(task_profile.get("requested_depth", "standard"))
                school_query = bool(task_profile.get("school_query")) or school_answer is not None
                synthesis_sentences = 12 if requested_depth == "detailed" else (9 if school_query else 6)
                reasoning_chars = 2800 if requested_depth == "detailed" else (2300 if school_query else 1700)
                grounded_result = synthesize_advanced_answer(
                    contextual_text, ranked_evidence, language=language,
                    task_profile=task_profile, max_sentences=synthesis_sentences,
                )
                grounded_candidate = str(grounded_result.get("response", "") or "").strip()
                reasoning_brief, advanced_reasoning = build_advanced_reasoning_brief(
                    contextual_text, language, task_profile, ranked_evidence,
                    deterministic_draft=grounded_candidate, max_chars=reasoning_chars,
                )
                if reasoning_brief:
                    evidence_packet = (
                        evidence_packet.rstrip()
                        + "\n\nREASONING BLUEPRINT (follow it; do not quote it):\n"
                        + reasoning_brief
                    ).strip()
                details["advanced_reasoning"] = advanced_reasoning
                details["grounded_candidate_confidence"] = float(grounded_result.get("confidence", 0.0) or 0.0)
                details["evidence_chars"] = len(evidence_packet)

                # Exact short definitions are usually more accurate when returned
                # directly.  All explanatory, comparative, technical and multi-hop
                # questions go through evidence-grounded synthesis when possible.
                direct_response = ""
                direct_details: dict = {}
                if common_answer is not None:
                    direct_response = common_answer
                    direct_details = {"route": "common_knowledge"}
                elif lexical_answer is not None and not lexical_answer.get("requires_generation") and task_profile.get("direct_ok"):
                    direct_response = str(lexical_answer.get("response", ""))
                    direct_details = {**lexical_answer}
                elif encyclopedia_answer is not None and task_profile.get("direct_ok") and language == "en":
                    direct_response = str(encyclopedia_answer.get("response", ""))
                    direct_details = {**encyclopedia_answer}
                elif school_answer is not None and task_profile.get("direct_ok") and not school_answer.get("requires_generation"):
                    direct_response = str(school_answer.get("response", ""))
                    direct_details = {**school_answer}
                elif universal_answer is not None and task_profile.get("direct_ok"):
                    direct_response = str(universal_answer.get("response", ""))
                    direct_details = {**universal_answer}

                # On the 135M emergency models, a high-confidence evidence-only
                # synthesis is often more accurate than asking the tiny model to
                # recreate the same facts. Stronger Qwen tiers still receive this
                # synthesis as a safe draft and can improve its wording.
                try:
                    active_model = self.local_llm.active_model
                except Exception:
                    active_model = "quality"
                grounded_confidence = float(grounded_result.get("confidence", 0.0) or 0.0)
                deterministic_tasks = {"factual_definition", "explanation", "comparison", "causal_explanation", "how_to"}
                if (
                    not direct_response and grounded_candidate and active_model in {"fast", "quality"}
                    and str(task_profile.get("task")) in deterministic_tasks
                    and grounded_confidence >= 0.72 and not task_profile.get("current_sensitive")
                ):
                    direct_response = grounded_candidate
                    direct_details = {"route": "advanced_grounded_direct", "grounded_confidence": grounded_confidence}

                use_synthesis = bool(task_profile.get("use_llm")) or smart_should_synthesize(task_profile, ranked_evidence, language)
                if direct_response and task_profile.get("direct_ok") and not task_profile.get("current_sensitive"):
                    use_synthesis = False

                if use_synthesis and self.llm_mode != "off" and self.local_llm.available:
                    try:
                        response, llm_details = self.ask_local_llm(
                            contextual_text, language, candidates, specialist=specialist,
                            extra_context=evidence_packet, task_profile=task_profile,
                        )
                        response = smart_clean_answer(response)
                        smart_validation = validate_smart_answer(response, original_text, language)
                        advanced_audit = audit_advanced_answer(
                            response, original_text, ranked_evidence, language=language,
                            task_profile=task_profile,
                        )
                        response, repair_details = choose_advanced_answer(
                            response, grounded_candidate, advanced_audit, language=language,
                        )
                        details.update(llm_details)
                        details["smart_validation"] = smart_validation
                        details["advanced_audit"] = advanced_audit
                        details["advanced_repair"] = repair_details
                        if repair_details.get("decision") != "generated_kept":
                            details["route"] = "advanced_grounded_repair"
                        if (
                            float(smart_validation.get("score", 0.0) or 0.0) < 0.30
                            and float(advanced_audit.get("score", 0.0) or 0.0) < 0.30
                            and not grounded_candidate
                        ):
                            response = ""
                            details["llm_rejected"] = True
                    except RuntimeError as error:
                        details["llm_error"] = str(error)

                if not response and direct_response:
                    response = direct_response
                    details.update(direct_details)
                    details["language"] = language
                    details["context_used"] = context_used

                if not response and grounded_candidate:
                    response = grounded_candidate
                    details.update({
                        "route": "advanced_grounded_fallback",
                        "grounded_confidence": float(grounded_result.get("confidence", 0.0) or 0.0),
                    })

                if not response:
                    qa_candidates = [item for item in candidates if item.get("kind") == "qa"]
                    best_qa = qa_candidates[0] if qa_candidates else None
                    if best_qa and int(best_qa.get("overlap", 0) or 0) >= 1 and float(best_qa.get("score", 0.0) or 0.0) >= 0.48:
                        response = str(best_qa.get("response", ""))
                        details.update({"route": "retrieval_qa", **best_qa})

                if not response:
                    document_candidates = [item for item in candidates if item.get("kind") == "document"]
                    best_document = document_candidates[0] if document_candidates else None
                    if best_document and int(best_document.get("overlap", 0) or 0) >= 1 and float(best_document.get("score", 0.0) or 0.0) >= 0.37:
                        response = extractive_document_answer(contextual_text, document_candidates, language) or str(best_document.get("response", ""))
                        details.update({"route": "retrieval_document", "candidates": document_candidates[:3]})

                if not response and ranked_evidence:
                    response = smart_extractive_fallback(
                        contextual_text, ranked_evidence, language=language,
                        task_profile=task_profile, max_sentences=5,
                    )
                    if response:
                        details["route"] = "smart_extractive_fallback"

                if not response and specialist_knowledge is not None:
                    response = str(specialist_knowledge.get("response", ""))
                    details.update({
                        "route": "specialist_model",
                        "specialist": specialist_knowledge.get("specialist"),
                        "specialist_match": specialist_knowledge.get("match_score"),
                    })

                if not response:
                    response, neural_details = self.neural_response(contextual_text, language)
                    details.update(neural_details)
                    details["route"] = "neural_last_resort" if neural_details.get("route") == "fallback" else neural_details.get("route", "neural")
                    if specialist is not None:
                        details["specialist_candidate"] = specialist

                if task_profile.get("current_sensitive") and details.get("route") in {
                    "smart_extractive_fallback", "retrieval_document", "retrieval_qa", "encyclopedia_direct",
                }:
                    warning = self.t(
                        "Note: this offline information may not reflect the latest changes.",
                        "Σημείωση: αυτές οι offline πληροφορίες μπορεί να μην περιλαμβάνουν τις πιο πρόσφατες αλλαγές.",
                        language,
                    )
                    response = response.rstrip() + "\n\n" + warning

        route_name = str(details.get("route", ""))
        response = smart_clean_answer(response)
        response = self.apply_persona(response, language, route_name, original_text)
        details["calibrated_confidence"] = calibrate_confidence(details, response)
        details["assistant_name"] = self.assistant_name
        details["persona_style"] = self.persona.get("style", "friendly")

        route_for_cache = str(details.get("route", ""))
        confidence_value = details.get("calibrated_confidence", 0.0)
        if isinstance(confidence_value, dict):
            confidence_for_cache = float(confidence_value.get("score", 0.0) or 0.0)
        else:
            confidence_for_cache = float(confidence_value or 0.0)
        if (
            route_for_cache != "response_cache"
            and not task_profile.get("current_sensitive")
            and confidence_for_cache >= 0.70
            and (
                "llm" in route_for_cache
                or "hybrid" in route_for_cache
                or route_for_cache in {"cascade", "consensus", "adaptive_quality", "expert"}
            )
        ):
            try:
                self.store.cache_response(original_text, language, response, route_for_cache, confidence_for_cache)
            except sqlite3.Error:
                pass

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

    def llm_context(
        self,
        candidates: Sequence[dict],
        query: str = "",
        language: str = "en",
        extra_context: str = "",
    ) -> str:
        """Build a compact, retrieval-first evidence packet for tiny models."""
        memories = self.store.list_memories(12)
        pieces: List[str] = []
        try:
            runtime = self.local_llm.runtime_settings()
            context_tokens = int(runtime.get("context", 512) or 512)
            output_tokens = int(runtime.get("max_tokens", 128) or 128)
        except Exception:
            context_tokens, output_tokens = 512, 128
        # Reserve room for ChatML, system rules, the question, and output.
        query_tokens = max(8, len(query) // 4)
        evidence_tokens = max(55, context_tokens - output_tokens - query_tokens - 125)
        char_budget = max(280, min(7000, int(evidence_tokens * 3.35)))
        extra_context = str(extra_context).strip()
        if extra_context:
            primary_budget = max(240, int(char_budget * 0.80))
            pieces.append(extra_context[:primary_budget])
        normalized_query = normalize_text(query)
        lexical_cues = {
            "define", "definition", "meaning", "means", "mean", "synonym", "antonym", "opposite",
            "word", "phrase", "translate", "etymology", "σημαινει", "ορισμος", "συνωνυμο",
            "αντωνυμο", "αντιθετο", "λεξη", "φραση", "μεταφραση",
        }
        is_lexical_question = any(cue in normalized_query for cue in lexical_cues)
        if is_lexical_question:
            universal_budget = max(60, int(char_budget * 0.10))
            lexical_budget = max(180, int(char_budget * 0.72))
            encyclopedia_budget = 0
        else:
            universal_budget = max(90, int(char_budget * 0.22))
            encyclopedia_budget = max(180, int(char_budget * 0.52))
            lexical_budget = max(70, int(char_budget * 0.13))

        evidence_sources = []
        try:
            indexed_facts = "" if extra_context else self.universal_knowledge.context(
                query, language=language, limit=8, max_chars=universal_budget
            )
        except Exception:
            indexed_facts = ""
        if indexed_facts:
            heading = "Curated offline facts:" if language != "el" else "Επιμελημένα offline στοιχεία:"
            evidence_sources.append(("universal", heading + "\n" + indexed_facts))

        try:
            encyclopedia_facts = "" if extra_context else self.encyclopedia_knowledge.context(
                query, language=language, limit=6, max_chars=encyclopedia_budget
            )
        except Exception:
            encyclopedia_facts = ""
        if encyclopedia_facts:
            evidence_sources.append(("encyclopedia", encyclopedia_facts))

        try:
            lexical_facts = "" if extra_context else self.lexical_knowledge.context(
                query, language=language, limit=7, max_chars=lexical_budget
            )
        except Exception:
            lexical_facts = ""
        if lexical_facts:
            heading = "Lexical and concept evidence:" if language != "el" else "Λεξιλογικά και εννοιολογικά στοιχεία:"
            evidence_sources.append(("lexical", heading + "\n" + lexical_facts))

        order = {"lexical": 0, "universal": 1, "encyclopedia": 2} if is_lexical_question else {"universal": 0, "encyclopedia": 1, "lexical": 2}
        evidence_sources.sort(key=lambda item: order.get(item[0], 9))
        pieces.extend(text for _, text in evidence_sources)

        used = sum(len(piece) + 2 for piece in pieces)
        remaining = max(0, char_budget - used)
        if remaining >= 140:
            if optimize_context is not None:
                try:
                    optimized = optimize_context(
                        query, candidates, memories, self.session_history,
                        max_chars=min(remaining, 1800),
                    )
                    if optimized:
                        pieces.append(optimized)
                except Exception:
                    pass
            else:
                for candidate in candidates[:3]:
                    response = str(candidate.get("response", "")).strip()
                    source = str(candidate.get("source", "")).strip()
                    if response:
                        pieces.append((f"Source: {source}\n" if source else "") + response[:600])

        used = sum(len(piece) + 2 for piece in pieces)
        remaining = max(0, char_budget - used)
        if memories and remaining >= 180:
            memory_text = "\n".join(f"{key} = {value}" for key, value in memories)
            pieces.append(("Saved user facts:\n" if language != "el" else "Αποθηκευμένα στοιχεία χρήστη:\n") + memory_text[:remaining])

        used = sum(len(piece) + 2 for piece in pieces)
        remaining = max(0, char_budget - used)
        if self.session_history and remaining >= 220:
            recent = list(self.session_history)[-4:]
            transcript = "\n".join(f"{role.title()}: {message[:280]}" for role, message in recent)
            pieces.append(("Recent conversation:\n" if language != "el" else "Πρόσφατη συνομιλία:\n") + transcript[:remaining])
        return "\n\n".join(pieces)[:char_budget]

    def set_hybrid_mode(self, mode: str) -> str:
        aliases = {
            "automatic": "auto", "best": "auto", "fast": "speed", "balanced": "smart",
            "verify": "cascade", "compare": "consensus", "dynamic": "adaptive",
            "specialist": "expert", "none": "off",
        }
        selected = aliases.get(mode.casefold().strip(), mode.casefold().strip())
        if selected not in HYBRID_MODES:
            raise ValueError("Hybrid mode must be auto, off, speed, smart, quality, adaptive, expert, consensus, or cascade.")
        self.hybrid_mode = selected
        self.store.set_setting("hybrid_mode", selected)
        return selected

    def query_complexity(self, text: str, specialist: Optional[dict] = None) -> float:
        words = word_tokens(text)
        normalized = normalize_text(text)
        score = min(0.34, len(words) / 95.0)
        cues = [
            "explain why", "compare", "analyze", "analyse", "step by step", "debug", "fix", "design",
            "summarize", "reason", "prove", "write code", "architecture", "tradeoff", "security",
            "εξηγησε", "συγκρινε", "αναλυσε", "βημα βημα", "διορθωσε", "σχεδιασε", "αποδειξε",
        ]
        planner = self.hybrid_components.get("planner", {})
        for language_cues in planner.get("complexity_cues", {}).values() if isinstance(planner, dict) else ():
            if isinstance(language_cues, list):
                cues.extend(str(cue) for cue in language_cues)
        score += min(0.40, sum(0.08 for cue in set(cues) if normalize_text(cue) in normalized))
        if specialist is not None:
            score += min(0.22, float(specialist.get("score", 0.0)) / 25.0)
        if any(char in text for char in ("```", "{", "}", "->", "=>")):
            score += 0.12
        if text.count("?") + text.count(";") >= 2:
            score += 0.08
        return max(0.0, min(1.0, score))

    def resolve_hybrid_plan(self, text: str, specialist: Optional[dict] = None) -> dict:
        self.local_llm.refresh()
        available_models = set(self.local_llm.model_paths)
        complexity = self.query_complexity(text, specialist)
        mode = self.hybrid_mode
        try:
            scan = scan_phone_hardware(self.data_dir, save=False, run_benchmark=False)
            saved_scan = load_device_profile(self.data_dir)
            saved_benchmark = (saved_scan or {}).get("processor", {}).get("benchmark")
            if isinstance(saved_benchmark, dict) and saved_benchmark.get("score"):
                scan["processor"]["benchmark"] = saved_benchmark
                family = {key: scan["processor"].get(key) for key in ("vendor", "family", "known_score", "matched_pattern")}
                scan["processor"]["score"] = _derive_cpu_score(
                    family, saved_benchmark, scan["processor"]["logical_cores"],
                    scan["processor"]["frequency"]["maximum_khz"], scan["processor"]["is_64_bit"]
                )
        except Exception:
            scan = {
                "ram": {"total": total_memory_bytes(), "available": available_memory_bytes()},
                "processor": {"score": 30, "is_64_bit": sys.maxsize > 2 ** 32},
                "thermal": _thermal_snapshot(), "battery": _battery_snapshot(),
                "storage": {"runtime": _storage_snapshot(self.data_dir)},
            }
        total = int(scan.get("ram", {}).get("total", 0) or 0)
        available = int(scan.get("ram", {}).get("available", 0) or 0)
        cpu_score = int(scan.get("processor", {}).get("score", 30) or 30)
        temperature = float(scan.get("thermal", {}).get("maximum_celsius", 0.0) or 0.0)
        pressure = _resource_pressure(scan)

        if not available_models or self.local_llm.binary_path is None or mode == "off":
            return {"mode": "off", "steps": [], "complexity": complexity, "reason": "GGUF runtime unavailable or hybrid mode disabled", "scan": scan}

        strongest = next((name for name in ("ultra", "smart", "quality", "fast") if name in available_models), None)
        compact = next((name for name in ("smart", "quality", "fast") if name in available_models and name != strongest), None)
        fastest = next((name for name in ("fast", "quality", "smart", "ultra") if name in available_models), strongest)

        resolved = mode
        if mode == "auto":
            if pressure["score"] >= 5 or temperature >= 52 or available < 300 * 1024 ** 2:
                resolved = "speed"
            elif "ultra" in available_models and total >= 5_200 * 1024 ** 2 and available >= 1_650 * 1024 ** 2 and cpu_score >= 48 and temperature < 46:
                resolved = "quality"
            elif "smart" in available_models and total >= 2_700 * 1024 ** 2 and available >= 760 * 1024 ** 2 and cpu_score >= 22 and temperature < 48:
                resolved = "quality"
            elif specialist is not None and ({"smart", "quality"} & available_models) and available >= 620 * 1024 ** 2 and temperature < 48:
                resolved = "expert"
            elif "quality" in available_models and available >= 520 * 1024 ** 2:
                resolved = "smart"
            else:
                resolved = "speed"

        if resolved in {"cascade", "adaptive", "consensus"}:
            minimum_available = {"adaptive": 1200, "cascade": 1300, "consensus": 1750}[resolved] * 1024 ** 2
            maximum_temperature = {"adaptive": 45, "cascade": 44, "consensus": 42}[resolved]
            if not compact or not strongest or compact == strongest or available < minimum_available or temperature >= maximum_temperature:
                resolved = "quality" if strongest else "speed"

        if resolved == "speed":
            steps = [fastest] if fastest else []
        elif resolved == "smart":
            model = "smart" if "smart" in available_models and available >= 700 * 1024 ** 2 else strongest
            steps = [model] if model else []
        elif resolved in {"quality", "expert"}:
            steps = [strongest] if strongest else []
        elif resolved in {"cascade", "adaptive", "consensus"}:
            steps = [compact, strongest] if compact and strongest and compact != strongest else ([strongest] if strongest else [])
        else:
            steps = []

        return {
            "mode": resolved,
            "requested_mode": mode,
            "steps": steps,
            "complexity": complexity,
            "available_ram": available,
            "total_ram": total,
            "cpu_score": cpu_score,
            "temperature_celsius": temperature,
            "pressure": pressure,
            "reason": f"complexity={complexity:.2f}, CPU={cpu_score}, free RAM={human_size(available)}, temperature={temperature:.1f}°C",
            "scan": scan,
        }

    @staticmethod
    def response_quality_score(response: str, language: str, question: str) -> dict:
        cleaned = response.strip()
        words = word_tokens(cleaned)
        score = 0.50
        issues: List[str] = []
        if not cleaned:
            return {"score": 0.0, "issues": ["empty response"]}
        detected = detect_language(cleaned)
        if detected not in {language, "neutral"}:
            score -= 0.45; issues.append("wrong output language")
        if len(words) < 4:
            score -= 0.22; issues.append("too short")
        elif len(words) >= 12:
            score += 0.10
        if len(cleaned) > 2800:
            score -= 0.08; issues.append("excessively long")
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        if lines and len(set(lines)) / len(lines) < 0.65:
            score -= 0.22; issues.append("repetitive lines")
        tokens = [normalize_text(token) for token in words]
        if len(tokens) >= 10 and len(set(tokens)) / len(tokens) < 0.36:
            score -= 0.18; issues.append("repetitive wording")
        uncertainty = ("i do not know", "i'm not sure", "δεν γνωριζω", "δεν ειμαι σιγουρ")
        if any(marker in normalize_text(cleaned) for marker in uncertainty):
            score -= 0.04
        query_terms = set(retrieval_terms(question))
        answer_terms = set(retrieval_terms(cleaned))
        if query_terms and answer_terms:
            overlap = len(query_terms & answer_terms) / max(1, min(len(query_terms), 8))
            score += min(0.18, overlap * 0.24)
        smart_check = validate_smart_answer(cleaned, question, language)
        score = 0.62 * score + 0.38 * float(smart_check.get("score", 0.5) or 0.5)
        issues.extend(str(item) for item in smart_check.get("issues", []) if str(item) not in issues)
        return {"score": max(0.0, min(1.0, score)), "issues": issues}

    def ask_local_llm(
        self,
        text: str,
        language: str,
        candidates: Sequence[dict] = (),
        specialist: Optional[dict] = None,
        extra_context: str = "",
        task_profile: Optional[dict] = None,
    ) -> Tuple[str, dict]:
        """Run the strongest safe plan inside one global answer deadline."""
        started = time.monotonic()
        deadline = started + MAX_ANSWER_SECONDS
        task_profile = task_profile or analyze_smart_query(text, language)
        context = self.llm_context(candidates, text, language, extra_context=extra_context)
        specialist_instruction = self.specialists.instruction(specialist, language)
        if specialist and str(specialist.get("id", "")).startswith("school_"):
            specialist_instruction = (self.school_tutor.instruction(language) + "\n" + specialist_instruction).strip()
        persona_text = self.persona_guidance(language)
        try:
            conversation_text = self.conversation_engine.instruction(text, language)
        except Exception:
            conversation_text = ""
        specialist_instruction = (persona_text + "\n" + conversation_text + "\n" + specialist_instruction).strip()
        plan = self.resolve_hybrid_plan(text, specialist)
        steps = list(plan.get("steps", []))
        mode = str(plan.get("mode", "smart"))
        if not steps:
            raise RuntimeError(str(plan.get("reason", "No compatible local GGUF model is available.")))
        if mode == "expert":
            specialist_instruction += self.t(
                "\nAct as a careful task expert. Use retrieved evidence first, verify the result, and make commands directly usable.",
                "\nΛειτούργησε ως προσεκτικός ειδικός. Χρησιμοποίησε πρώτα τα ανακτημένα στοιχεία, έλεγξε το αποτέλεσμα και δώσε άμεσα χρήσιμες εντολές.",
                language,
            )

        first_model = steps[0]
        first_runtime = self.local_llm.runtime_settings(first_model)
        profile = str(first_runtime.get("resolved", "entry"))
        # Very slow profiles benefit more from one complete pass than two short,
        # truncated passes. Multi-pass verification remains available on stronger phones.
        if len(steps) > 1 and profile not in {"balanced", "performance"}:
            steps = [first_model]
            mode = "smart" if mode in {"adaptive", "cascade", "consensus"} else mode

        remaining = max(5.0, deadline - time.monotonic() - 2.0)
        first_budget = remaining
        if len(steps) > 1:
            first_budget = min(62.0, max(28.0, remaining - 25.0))
        draft = self.local_llm.generate(
            text, language, context=context,
            max_tokens=max(int(first_runtime.get("max_tokens", 192) or 192), 300 if str(task_profile.get("requested_depth")) == "detailed" else (240 if task_profile.get("school_query") else 192)),
            specialist_instruction=specialist_instruction,
            model_name=first_model,
            time_budget_seconds=first_budget,
            task_profile=task_profile,
        )
        draft_quality = self.response_quality_score(draft, language, text)
        final = draft
        final_model = first_model
        passes = [{"model": first_model, "quality": draft_quality, "role": "draft", "budget_seconds": round(first_budget, 1)}]
        degraded = False
        second_pass_skipped = False
        consensus_details: dict = {}

        if len(steps) > 1:
            adaptive_threshold = float(self.hybrid_components.get("adaptive", {}).get("draft_accept_score", 0.80) or 0.80)
            if mode == "adaptive" and draft_quality["score"] >= adaptive_threshold and float(plan.get("complexity", 0.0)) < 0.72:
                second_pass_skipped = True
            available_after = available_memory_bytes()
            temperature_after = float(_thermal_snapshot().get("maximum_celsius", 0.0) or 0.0)
            minimum_ram = 760 * 1024 ** 2 if mode == "adaptive" else 900 * 1024 ** 2
            if mode == "consensus":
                minimum_ram = 1_100 * 1024 ** 2
            remaining = deadline - time.monotonic() - 2.0
            if remaining < 10.0:
                second_pass_skipped = True
                degraded = True
            if not second_pass_skipped and ((available_after and available_after < minimum_ram) or temperature_after >= (44.0 if mode == "consensus" else 46.0)):
                degraded = True
            elif not second_pass_skipped:
                if mode == "consensus":
                    second_prompt = self.t(
                        "Answer the original question independently. Use the retrieved evidence, verify facts and logic, and return only the best final answer.",
                        "Απάντησε ανεξάρτητα στην αρχική ερώτηση. Χρησιμοποίησε τα ανακτημένα στοιχεία, έλεγξε τα γεγονότα και τη λογική και επέστρεψε μόνο την καλύτερη τελική απάντηση.",
                        language,
                    ) + "\n\n" + text[:1500]
                else:
                    second_prompt = self.t(
                        "Check the draft against the original question and retrieved evidence. Correct factual, logical, mathematical, command, and language errors. Remove repetition. Return only the improved answer.\n\nQuestion:\n{question}\n\nDraft:\n{draft}",
                        "Έλεγξε το πρόχειρο με βάση την αρχική ερώτηση και τα ανακτημένα στοιχεία. Διόρθωσε πραγματολογικά, λογικά, μαθηματικά, τεχνικά και γλωσσικά λάθη. Αφαίρεσε επαναλήψεις. Επίστρεψε μόνο τη βελτιωμένη απάντηση.\n\nΕρώτηση:\n{question}\n\nΠρόχειρο:\n{draft}",
                        language,
                    ).format(question=text[:1200], draft=draft[:1800])
                try:
                    second_budget = max(8.0, deadline - time.monotonic() - 2.0)
                    refined = self.local_llm.generate(
                        second_prompt, language, context=context,
                        max_tokens=240,
                        specialist_instruction=specialist_instruction + " Verify carefully and do not preserve an error just because it appears in the draft.",
                        model_name=steps[1],
                        time_budget_seconds=second_budget,
                        task_profile=task_profile,
                    )
                    refined_quality = self.response_quality_score(refined, language, text)
                    passes.append({"model": steps[1], "quality": refined_quality, "role": "independent" if mode == "consensus" else "verification", "budget_seconds": round(second_budget, 1)})
                    if mode == "consensus" and choose_consensus is not None:
                        final, consensus_details = choose_consensus(text, draft, refined, draft_quality, refined_quality)
                        final_model = steps[1] if final == refined else first_model
                    elif refined_quality["score"] + 0.04 >= draft_quality["score"]:
                        final = refined
                        final_model = steps[1]
                    else:
                        degraded = True
                except RuntimeError:
                    degraded = True

        final_quality = self.response_quality_score(final, language, text)
        elapsed = time.monotonic() - started
        return final, {
            "route": "hybrid_" + mode,
            "language": language,
            "llm_mode": self.llm_mode,
            "hybrid_mode": self.hybrid_mode,
            "hybrid_plan": {key: value for key, value in plan.items() if key != "scan"},
            "passes": passes,
            "second_pass_skipped": second_pass_skipped,
            "degraded_to_safe_result": degraded,
            "consensus": consensus_details,
            "final_quality": final_quality,
            "model": str(self.local_llm.model_paths.get(final_model) or self.local_llm.model_paths.get(first_model) or "missing"),
            "model_profile": final_model,
            "context_chars": len(context),
            "answer_deadline_seconds": MAX_ANSWER_SECONDS,
            "inference_elapsed_seconds": round(elapsed, 3),
            "specialist": specialist.get("id") if specialist else None,
            "persona_style": self.persona.get("style", "friendly"),
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
            f"  Hybrid mode:         {self.hybrid_mode}",
            f"  AI name/persona:     {self.assistant_name} / {self.persona.get('style', 'friendly')}",
            f"  Human conversation: {'enabled' if self.persona.get('human_style', True) else 'disabled'}",
            f"  Runtime modules:     {sum(1 for name in ('persona_engine', 'context_optimizer', 'consensus_engine', 'confidence_engine', 'resource_advisor', 'universal_knowledge', 'lexical_knowledge', 'encyclopedia_knowledge', 'conversation_engine', 'resource_matrix', 'advanced_reasoning') if name in sys.modules)}/11 loaded",
            f"  Universal knowledge: {getattr(self.universal_knowledge, 'entry_count', len(getattr(self.universal_knowledge, 'entries', []))):,} indexed bilingual entries",
            f"  Lexical concepts:    {getattr(self.lexical_knowledge, 'entry_count', 0):,} WordNet concepts / {getattr(self.lexical_knowledge, 'greek_count', 0):,} Greek-linked",
            f"  Encyclopedia:        {getattr(self.encyclopedia_knowledge, 'article_count', 0):,} articles / {getattr(self.encyclopedia_knowledge, 'chunk_count', 0):,} passages",
            f"  Answer deadline:     {MAX_ANSWER_SECONDS:.0f}s maximum local-inference plan",
            f"  Active GGUF model:   {self.local_llm.active_model}",
            f"  CPU runtime profile: {self.local_llm.requested_cpu_profile} -> {self.local_llm.runtime_settings()['resolved']}",
            f"  Live combination:    {self.local_llm.runtime_settings().get('combination_id', 'unknown')}",
            f"  Active model size:   {human_size(self.local_llm.model_path.stat().st_size) if self.local_llm.model_path and self.local_llm.model_path.is_file() else 'packaged in split parts'}",
            f"  Available GGUF models: {len(self.local_llm.model_paths)}/{len(EXTERNAL_LLM_MODELS)} detected",
            f"  Specialist models:   {sum(1 for item in self.specialists.status() if item['loaded'])}/{len(self.specialists.FILES)} loaded",
            f"  School foundation:   grades 1-12 shared across every model",
            f"  Hybrid controllers:  {len(self.hybrid_components)}/{len(HYBRID_COMPONENT_FILES)} loaded",
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
  /persona                      Show AI name and conversation personality
  /name NAME                    Change the AI name
  /style friendly|calm_expert|casual|mentor|direct
                                Change human conversation style
  /human on|off                 Enable or disable natural wording
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
  /school [GRADE] [SUBJECT]     Show grade 1-12 school help or a subject overview
  /knowledge                    Show the shared bilingual knowledge foundation
  /matrix                       Show the live hardware/model tuning plan
  /dork QUERY                   Safely search public web pages and learn them
  /web-learn QUERY              No-key Bing RSS + Wikipedia learning; supports safe operators
  /google-ai                    Explain why Gemini requires credentials
  /summarize PATH               Create an extractive summary of a text file
  /remember KEY = VALUE         Store a persistent local memory
  /memories                     List saved memories
  /forget KEY                   Delete one persistent memory
  /train                        Retrain the neural intent model
  /build-lm [PATH]              Build the experimental local generator
  /generate [PROMPT]            Generate with the bundled bilingual MicroLM
  /llm off|fallback|always      Control when transformer inference is allowed
  /hybrid auto|off|speed|smart|quality|adaptive|expert|consensus|cascade
                                Select resource-aware hybrid orchestration
  /llm-model fast|quality|smart|ultra
                                Select 135M, Qwen3 0.6B, or Qwen3 1.7B
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
  /προσωπικότητα                 Προβολή ονόματος και προσωπικότητας AI
  /όνομα ΟΝΟΜΑ                  Αλλαγή ονόματος AI
  /στυλ friendly|calm_expert|casual|mentor|direct
                                Αλλαγή φυσικού τρόπου συζήτησης
  /ανθρώπινο on|off             Ενεργοποίηση ή απενεργοποίηση φυσικής διατύπωσης
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
  /school [ΤΑΞΗ] [ΜΑΘΗΜΑ]       Βοήθεια σχολείου για τάξεις 1-12
  /knowledge                    Εμφάνιση της κοινής δίγλωσσης βάσης γνώσης
  /matrix                       Εμφάνιση του ζωντανού πλάνου hardware/μοντέλου
  /dork ΕΡΩΤΗΜΑ                  Ασφαλής έρευνα δημόσιου ιστού και μάθηση
  /web-learn ΕΡΩΤΗΜΑ             Μάθηση χωρίς API key από Bing RSS + Wikipedia
  /google-ai                    Επεξήγηση γιατί το Gemini απαιτεί διαπιστευτήρια
  /σύνοψη ΔΙΑΔΡΟΜΗ              Εξαγωγική σύνοψη αρχείου κειμένου
  /remember ΚΛΕΙΔΙ = ΤΙΜΗ       Αποθήκευση μόνιμης μνήμης
  /memories                     Προβολή αποθηκευμένων μνημών
  /forget ΚΛΕΙΔΙ                Διαγραφή μνήμης
  /train                        Επανεκπαίδευση νευρωνικού μοντέλου
  /build-lm [ΔΙΑΔΡΟΜΗ]          Δημιουργία πειραματικού generator
  /generate [PROMPT]            Παραγωγή με το ενσωματωμένο MicroLM
  /llm off|fallback|always      Έλεγχος χρήσης του τοπικού transformer
  /υβριδικό auto|off|speed|smart|quality|adaptive|expert|consensus|cascade
                                Επιλογή υβριδικής δρομολόγησης
  /μοντέλο fast|quality|smart|ultra
                                Επιλογή 135M, Qwen3 0.6B ή Qwen3 1.7B
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
        "/σχολείο": "/school", "/σχολειο": "/school", "/τάξη": "/school", "/ταξη": "/school",
        "/γνώσεις": "/knowledge", "/γνωσεις": "/knowledge",
        "/πίνακας": "/matrix", "/πινακας": "/matrix", "/hardware": "/matrix",
        "/μοντέλο": "/llm-model", "/μοντελο": "/llm-model",
        "/μοντέλα": "/models", "/μοντελα": "/models",
        "/επεξεργαστησ": "/cpu-profile", "/επεξεργαστής": "/cpu-profile", "/cpu": "/cpu-profile",
        "/λειτουργια-llm": "/llm", "/λειτουργία-llm": "/llm",
        "/υβριδικο": "/hybrid", "/υβριδικό": "/hybrid", "/hybrid-mode": "/hybrid",
        "/εξοδοσ": "/quit", "/έξοδοσ": "/quit", "/εξοδος": "/quit",
        "/γλωσσα": "/language", "/γλώσσα": "/language",
        "/προσωπικοτητα": "/persona", "/προσωπικότητα": "/persona",
        "/ονομα": "/name", "/όνομα": "/name",
        "/στυλ": "/style", "/ανθρωπινο": "/human", "/ανθρώπινο": "/human",
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
    if command == "/persona":
        return True, describe_persona(assistant.persona, language)
    if command == "/name":
        if not argument:
            return True, assistant.t("Usage: /name AI_NAME", "Χρήση: /όνομα ΟΝΟΜΑ_AI", language)
        assistant.update_persona(assistant_name=argument)
        return True, assistant.t(
            f"My name is now {assistant.assistant_name}.",
            f"Το όνομά μου είναι πλέον {assistant.assistant_name}.", language,
        )
    if command == "/style":
        if not argument:
            choices = ", ".join(PERSONA_STYLES)
            return True, assistant.t(f"Current style: {assistant.persona.get('style')}. Choices: {choices}", f"Τρέχον στυλ: {assistant.persona.get('style')}. Επιλογές: {choices}", language)
        try:
            assistant.update_persona(style=argument)
            return True, assistant.t(f"Conversation style set to {assistant.persona.get('style')}.", f"Το στυλ συζήτησης ορίστηκε σε {assistant.persona.get('style')}.", language)
        except ValueError as error:
            return True, assistant.t(str(error), "Άγνωστο στυλ. Χρησιμοποίησε friendly, calm_expert, casual, mentor ή direct.", language)
    if command == "/human":
        if not argument:
            state = "on" if assistant.persona.get("human_style", True) else "off"
            return True, assistant.t(f"Human-like wording is {state}.", f"Η φυσική διατύπωση είναι {state}.", language)
        normalized = normalize_text(argument)
        if normalized not in {"on", "off", "yes", "no", "ενεργο", "ανενεργο", "ναι", "οχι"}:
            return True, assistant.t("Usage: /human on|off", "Χρήση: /ανθρώπινο on|off", language)
        enabled = normalized in {"on", "yes", "ενεργο", "ναι"}
        assistant.update_persona(human_style=enabled)
        return True, assistant.t(f"Human-like wording {'enabled' if enabled else 'disabled'}.", f"Η φυσική διατύπωση {'ενεργοποιήθηκε' if enabled else 'απενεργοποιήθηκε'}.", language)
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
            f"Hybrid orchestration: {assistant.hybrid_mode}",
            "",
        ]
        lines_el = [
            "Κατάλογος ενσωματωμένων μοντέλων AI",
            f"Ενεργός νευρωνικός classifier: {selected_classifier}",
            f"Ενεργό GGUF μοντέλο: {selected_gguf}",
            f"Παραλλαγή MicroLM: {assistant.micro_model_variant}",
            f"Υβριδική δρομολόγηση: {assistant.hybrid_mode}",
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
            assistant.t(f"Fast GGUF package: {Path(__file__).resolve().parent / 'Models' / SPLIT_GGUF_DIRNAME}", f"Πακέτο γρήγορου GGUF: {Path(__file__).resolve().parent / 'Models' / SPLIT_GGUF_DIRNAME}", language),
            assistant.t(f"Quality GGUF cache: {assistant.data_dir / GGUF_CACHE_DIRNAME}", f"Cache ποιοτικού GGUF: {assistant.data_dir / GGUF_CACHE_DIRNAME}", language),
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
    if command == "/matrix":
        runtime = assistant.local_llm.runtime_settings()
        device = assistant.local_llm.device_info
        guards = ", ".join(runtime.get("guards", [])) or assistant.t("none", "κανένας", language)
        return True, assistant.t(
            "Live hardware/model plan:\n"
            f"Combination: {runtime.get('combination_id', 'unknown')}\n"
            f"Model: {runtime.get('model')}\n"
            f"CPU score: {device.get('processor_score', '?')} / cores: {device.get('cpu_count', '?')}\n"
            f"RAM: {human_size(runtime.get('available_ram', 0))} available of {human_size(runtime.get('total_ram', 0))}\n"
            f"Threads/context/batch/ubatch/tokens: {runtime.get('threads')}/{runtime.get('context')}/{runtime.get('batch')}/{runtime.get('ubatch')}/{runtime.get('max_tokens')}\n"
            f"Thermal guards: {guards}",
            "Ζωντανό πλάνο hardware/μοντέλου:\n"
            f"Συνδυασμός: {runtime.get('combination_id', 'unknown')}\n"
            f"Μοντέλο: {runtime.get('model')}\n"
            f"CPU score: {device.get('processor_score', '?')} / πυρήνες: {device.get('cpu_count', '?')}\n"
            f"RAM: {human_size(runtime.get('available_ram', 0))} διαθέσιμη από {human_size(runtime.get('total_ram', 0))}\n"
            f"Threads/context/batch/ubatch/tokens: {runtime.get('threads')}/{runtime.get('context')}/{runtime.get('batch')}/{runtime.get('ubatch')}/{runtime.get('max_tokens')}\n"
            f"Δικλείδες: {guards}", language
        )

    if command == "/knowledge":
        return True, (
            assistant.universal_knowledge.catalog(language) + "\n"
            + assistant.lexical_knowledge.catalog(language) + "\n"
            + assistant.encyclopedia_knowledge.catalog(language)
        )

    if command == "/school":
        if not argument:
            return True, assistant.school_tutor.catalog(language) + assistant.t(
                "\nExamples: /school 5 math, /school 9 science, or ask: explain fractions.",
                "\nΠαραδείγματα: /school 5 μαθηματικά, /school 9 επιστήμες ή ρώτησε: εξήγησε τα κλάσματα.",
                language
            )
        match = re.match(r"\s*(1[0-2]|[1-9])(?:\s+(.+))?$", argument.strip())
        if not match:
            return True, assistant.t(
                "Use /school followed by grade 1-12 and optionally a subject.",
                "Χρησιμοποίησε /school με τάξη 1-12 και προαιρετικά μάθημα.",
                language
            )
        return True, assistant.school_tutor.grade_overview(int(match.group(1)), (match.group(2) or "").strip(), language)
    if command == "/google-ai":
        return True, assistant.t(
            "Google Gemini cannot be called anonymously: its official API requires credentials. Pocket AI instead learns without an API key from public Bing RSS search results, Wikipedia, and readable public pages through /web-learn.",
            "Το Google Gemini δεν μπορεί να κληθεί ανώνυμα: το επίσημο API του απαιτεί διαπιστευτήρια. Το Pocket AI μαθαίνει χωρίς API key από δημόσια αποτελέσματα Bing RSS, Wikipedia και αναγνώσιμες δημόσιες σελίδες μέσω /web-learn.",
            language
        )
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
    if command == "/hybrid":
        if not argument:
            return True, assistant.t(
                f"Hybrid mode: {assistant.hybrid_mode}. Use auto, off, speed, smart, quality, adaptive, expert, consensus, or cascade.",
                f"Υβριδική λειτουργία: {assistant.hybrid_mode}. Χρησιμοποίησε auto, off, speed, smart, quality, adaptive, expert, consensus ή cascade.",
                language,
            )
        try:
            selected = assistant.set_hybrid_mode(argument)
            return True, assistant.t(
                f"Hybrid mode set to {selected}: {HYBRID_MODES[selected]}",
                f"Η υβριδική λειτουργία ορίστηκε σε {selected}: {HYBRID_MODES_EL[selected]}",
                language,
            )
        except ValueError as error:
            return True, assistant.t(str(error), "Η λειτουργία πρέπει να είναι auto, off, speed, smart, quality, adaptive, expert, consensus ή cascade.", language)
    if command == "/llm-model":
        if not argument:
            return True, assistant.t(
                f"Active model: {assistant.local_llm.active_model}. Use /llm-model fast, quality, smart, or ultra.",
                f"Ενεργό μοντέλο: {assistant.local_llm.active_model}. Χρησιμοποίησε /llm-model fast, quality, smart ή ultra.",
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
            f"Hybrid mode: {assistant.hybrid_mode}",
            f"llama.cpp: {status['binary']}",
            f"CPU profile: {status['cpu_profile_requested']} -> {status['cpu_profile_resolved']}",
            f"Runtime: threads={runtime['threads']}, context={runtime['context']}, batch={runtime['batch']}, ubatch={runtime['ubatch']}, token cap={runtime['max_tokens']}",
            f"Detected device: {device_name}; processor family={marker}; available RAM={human_size(runtime['available_ram'])}",
        ]
        lines_el = [
            f"GGUF έτοιμο: {status['available']}",
            f"Ενεργό μοντέλο: {status['active_model']}",
            f"Λειτουργία: {assistant.llm_mode}",
            f"Υβριδική λειτουργία: {assistant.hybrid_mode}",
            f"llama.cpp: {status['binary']}",
            f"Profile επεξεργαστή: {status['cpu_profile_requested']} -> {status['cpu_profile_resolved']}",
            f"Ρυθμίσεις: νήματα={runtime['threads']}, context={runtime['context']}, batch={runtime['batch']}, ubatch={runtime['ubatch']}, όριο tokens={runtime['max_tokens']}",
            f"Συσκευή: {device_name}; οικογένεια επεξεργαστή={marker}; διαθέσιμη RAM={human_size(runtime['available_ram'])}",
        ]
        for key in ("fast", "quality", "smart", "ultra"):
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


SIMPLE_HELP_TRIGGERS = {
    "help", "help me", "options", "show options", "menu", "commands",
    "βοηθεια", "βοήθεια", "βοηθησε με", "βοήθησέ με", "μενου", "μενού",
    "επιλογες", "επιλογές", "εντολες", "εντολές",
}

PLAIN_EXIT_TRIGGERS = {
    "exit", "quit", "close", "goodbye", "bye",
    "εξοδος", "έξοδος", "κλεισε", "κλείσε", "αντιο", "αντίο",
}

PLAIN_SCAN_TRIGGERS = {
    "scan phone", "scan my phone", "check my phone", "find best model",
    "choose best model", "select best model", "scan device",
    "σαρωση κινητου", "σάρωση κινητού", "ελεγξε το κινητο", "έλεγξε το κινητό",
    "βρες το καλυτερο μοντελο", "βρες το καλύτερο μοντέλο",
}

PLAIN_PERSONA_TRIGGERS = {
    "change your name", "name the ai", "name ai", "change ai name",
    "change personality", "humanize ai",
    "αλλαξε ονομα", "άλλαξε όνομα", "ονομασε το ai", "ονόμασε το ai",
    "αλλαξε προσωπικοτητα", "άλλαξε προσωπικότητα",
}


def _easy_scan_and_apply(assistant: PocketAssistant, language: str) -> str:
    print(assistant.t(
        "Scanning the phone and checking available RAM and storage...",
        "Γίνεται σάρωση του κινητού, της διαθέσιμης RAM και του χώρου...",
        language,
    ))
    scan = scan_phone_hardware(assistant.data_dir, save=True, run_benchmark=True)
    recommendation = scan.get("recommendation", {})
    selected_model = str(recommendation.get("gguf_model", "internal"))
    runtime_profile = str(recommendation.get("runtime_profile", "auto"))
    hybrid_mode = str(recommendation.get("hybrid_mode", DEFAULT_HYBRID_MODE))

    try:
        assistant.set_llm_cpu_profile(runtime_profile)
    except (OSError, ValueError):
        pass
    if hybrid_mode in HYBRID_MODES:
        try:
            assistant.set_hybrid_mode(hybrid_mode)
        except ValueError:
            pass
    if selected_model in EXTERNAL_LLM_MODELS:
        try:
            assistant.set_llm_model(selected_model)
            assistant.set_llm_mode("always")
        except (OSError, ValueError):
            assistant.set_llm_mode("off")
            selected_model = "internal"
    else:
        assistant.set_llm_mode("off")

    total_ram = human_size(int(scan.get("ram", {}).get("total", 0) or 0))
    available_ram = human_size(int(scan.get("ram", {}).get("available", 0) or 0))
    storage_free = human_size(int(scan.get("storage", {}).get("runtime", {}).get("free", 0) or 0))
    if language == "el":
        return (
            "Η σάρωση ολοκληρώθηκε.\n"
            f"RAM: {total_ram} συνολικά, {available_ram} διαθέσιμα\n"
            f"Ελεύθερος χώρος: {storage_free}\n"
            f"Επιλεγμένο μοντέλο: {selected_model}\n"
            f"Runtime: {runtime_profile}\n"
            f"Υβριδική λειτουργία: {hybrid_mode}\n"
            "Οι ασφαλείς ρυθμίσεις εφαρμόστηκαν σε αυτή τη συνομιλία."
        )
    return (
        "Scan complete.\n"
        f"RAM: {total_ram} total, {available_ram} available\n"
        f"Free storage: {storage_free}\n"
        f"Selected model: {selected_model}\n"
        f"Runtime: {runtime_profile}\n"
        f"Hybrid mode: {hybrid_mode}\n"
        "The safe settings were applied to this conversation."
    )


def easy_help_menu(assistant: PocketAssistant, language: str) -> bool:
    """Open a simple numbered menu after the user types help."""
    if language == "el":
        print("\nΤι θέλεις να κάνεις;")
        print("  1. Επιστροφή στη συνομιλία")
        print("  2. Σάρωση κινητού και αυτόματη επιλογή καλύτερου μοντέλου")
        print("  3. Αλλαγή ονόματος και τρόπου ομιλίας του AI")
        print("  4. Δίδαξε στο AI μία ερώτηση και απάντηση")
        print("  5. Μάθηση από αρχείο ή φάκελο")
        print("  6. Ασφαλής έρευνα στο διαδίκτυο και μάθηση")
        print("  7. Σχολικός βοηθός για τάξεις 1-12")
        print("  8. Προβολή ενεργού μοντέλου και κατάστασης")
        print("  9. Προβολή προχωρημένων εντολών")
        print("  10. Έξοδος")
        menu_prompt = "Επίλεξε 1-10: "
    else:
        print("\nWhat would you like to do?")
        print("  1. Return to chat")
        print("  2. Scan phone and automatically choose the best model")
        print("  3. Change the AI name and speaking style")
        print("  4. Teach the AI a question and answer")
        print("  5. Learn from a file or folder")
        print("  6. Safely research the web and learn")
        print("  7. School tutor for grades 1-12")
        print("  8. Show active model and status")
        print("  9. Show advanced commands")
        print("  10. Exit")
        menu_prompt = "Choose 1-10: "

    try:
        choice = input(menu_prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return True

    if choice in {"", "1"}:
        return True
    if choice == "2":
        print(_easy_scan_and_apply(assistant, language))
        return True
    if choice == "3":
        configure_persona_menu(assistant.data_dir)
        assistant.persona = load_persona(assistant.data_dir)
        print(assistant.t(
            f"Done. My name is {assistant.assistant_name}.",
            f"Έτοιμο. Το όνομά μου είναι {assistant.assistant_name}.",
            language,
        ))
        return True
    if choice == "4":
        try:
            question = input("Question: " if language != "el" else "Ερώτηση: ").strip()
            answer = input("Answer: " if language != "el" else "Απάντηση: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return True
        if not question or not answer:
            print(assistant.t("Nothing was saved.", "Δεν αποθηκεύτηκε κάτι.", language))
            return True
        if detect_language(question) == "unsupported" or detect_language(answer) == "unsupported":
            print(assistant.t(
                "Teaching supports English and Greek only.",
                "Η εκμάθηση υποστηρίζει μόνο Αγγλικά και Ελληνικά.",
                language,
            ))
            return True
        item_id = assistant.store.teach(question, answer)
        print(assistant.t(
            f"Learned and saved locally as item {item_id}.",
            f"Το έμαθα και αποθηκεύτηκε τοπικά ως στοιχείο {item_id}.",
            language,
        ))
        return True
    if choice == "5":
        try:
            raw_path = input(
                "File or folder path: " if language != "el" else "Διαδρομή αρχείου ή φακέλου: "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return True
        if not raw_path:
            return True
        try:
            result = ingest_path(assistant.store, Path(raw_path).expanduser())
            print(assistant.t(
                f"Indexed {result['files_indexed']} file(s) and added {result['chunks_added']} knowledge chunks.",
                f"Έγινε ευρετηρίαση {result['files_indexed']} αρχείου/ων και προστέθηκαν {result['chunks_added']} τμήματα γνώσης.",
                language,
            ))
        except (OSError, ValueError) as error:
            print(assistant.t(
                f"Could not learn from that path: {error}",
                f"Δεν ήταν δυνατή η μάθηση από αυτή τη διαδρομή: {error}",
                language,
            ))
        return True
    if choice == "6":
        try:
            query = input(
                "Public research topic: " if language != "el" else "Θέμα δημόσιας έρευνας: "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return True
        if not query:
            return True
        try:
            result = assistant.web_research.learn(query, max_pages=3)
            print(assistant.t(
                f"Research complete: {len(result['results'])} result(s), {result['pages']} page(s), "
                f"{result['chunks']} knowledge chunks saved.",
                f"Η έρευνα ολοκληρώθηκε: {len(result['results'])} αποτέλεσμα/τα, {result['pages']} σελίδα/ες "
                f"και {result['chunks']} τμήματα γνώσης αποθηκεύτηκαν.",
                language,
            ))
        except (OSError, ValueError) as error:
            print(assistant.t(
                f"Web learning failed: {error}",
                f"Η μάθηση από το διαδίκτυο απέτυχε: {error}",
                language,
            ))
        return True
    if choice == "7":
        try:
            grade_raw = input("Grade 1-12: " if language != "el" else "Τάξη 1-12: ").strip()
            subject = input("Subject (optional): " if language != "el" else "Μάθημα (προαιρετικό): ").strip()
            grade = int(grade_raw)
            if grade < 1 or grade > 12:
                raise ValueError
            print(assistant.school_tutor.grade_overview(grade, subject, language))
        except (ValueError, EOFError, KeyboardInterrupt):
            print(assistant.t("Enter a grade from 1 to 12.", "Δώσε τάξη από 1 έως 12.", language))
        return True
    if choice == "8":
        print("\n" + assistant.stats_text())
        return True
    if choice == "9":
        print("\n" + (HELP_TEXT_EL if language == "el" else HELP_TEXT_EN))
        return True
    if choice == "10":
        return False

    print(assistant.t("Choose a number from 1 to 10.", "Επίλεξε αριθμό από 1 έως 10.", language))
    return True


def chat_loop(assistant: PocketAssistant) -> None:
    if assistant.language_mode == "el":
        print(f"\n{assistant.assistant_name} είναι έτοιμο. Ρώτησέ με οτιδήποτε ή γράψε help για επιλογές.")
    elif assistant.language_mode == "en":
        print(f"\n{assistant.assistant_name} is ready. Ask me anything, or type help for options.")
    else:
        print(f"\n{assistant.assistant_name} is ready / είναι έτοιμο. Ask anything, or type help / βοήθεια.")

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

        normalized_plain = normalize_text(text.lstrip("/"))
        detected_language = "el" if GREEK_CHAR_RE.search(text) else assistant.last_language
        if assistant.language_mode in SUPPORTED_LANGUAGES:
            detected_language = assistant.language_mode

        if normalized_plain in SIMPLE_HELP_TRIGGERS:
            if not easy_help_menu(assistant, detected_language):
                farewell = assistant.t("Goodbye.", "Αντίο.", detected_language)
                print(f"{assistant.assistant_name}: {farewell}")
                return
            continue
        if normalized_plain in PLAIN_EXIT_TRIGGERS:
            farewell = assistant.t("Goodbye.", "Αντίο.", detected_language)
            print(f"{assistant.assistant_name}: {farewell}")
            return
        if normalized_plain in PLAIN_SCAN_TRIGGERS:
            print(f"{assistant.assistant_name}: {_easy_scan_and_apply(assistant, detected_language)}")
            continue
        if normalized_plain in PLAIN_PERSONA_TRIGGERS:
            configure_persona_menu(assistant.data_dir)
            assistant.persona = load_persona(assistant.data_dir)
            print(
                f"{assistant.assistant_name}: "
                + assistant.t("Ready. Ask me anything.", "Έτοιμο. Ρώτησέ με οτιδήποτε.", detected_language)
            )
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
        "--hybrid", dest="hybrid_mode", choices=tuple(HYBRID_MODES), default=DEFAULT_HYBRID_MODE,
        help="Hybrid inference mode including adaptive, expert, consensus, and cascade.",
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
    simple_startup = len(sys.argv) == 1

    # Normal launch enters chat immediately. Hardware matching is automatic.
    if simple_startup:
        scan = automatic_startup_scan(
            data_dir,
            quiet=load_device_profile(data_dir) is not None,
        )
        recommendation = scan.get("recommendation", {})
        args.profile = str(recommendation.get("classifier_profile", "balanced"))
        args.cpu_profile = str(recommendation.get("runtime_profile", "auto"))
        args.hybrid_mode = str(recommendation.get("hybrid_mode", DEFAULT_HYBRID_MODE))

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
        profile = MODEL_PROFILES[profile_name]
        if not simple_startup:
            print_banner(profile_name)
            print(profile["description"])
            print(f"Data: {data_dir}")
            if recommendation:
                print(
                    f"Automatic match: model={recommendation.get('gguf_model')}, "
                    f"runtime={recommendation.get('runtime_profile')}, classifier={profile_name}, hybrid={recommendation.get('hybrid_mode')}."
                )
        installed_pretrained = bootstrap_pretrained_model(dataset_path, model_path, metadata_path, profile_name)
        if installed_pretrained and not simple_startup:
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
            if getattr(args, "hybrid_mode", None):
                assistant.set_hybrid_mode(args.hybrid_mode)
            runtime = assistant.local_llm.runtime_settings()
            if not simple_startup:
                print(
                    f"GGUF CPU profile: {assistant.local_llm.requested_cpu_profile} -> {runtime['resolved']} "
                    f"({runtime['threads']} thread(s), context {runtime['context']}, batch {runtime['batch']}); "
                    f"hybrid={assistant.hybrid_mode}."
                )
            if recommendation:
                selected_model = str(recommendation.get("gguf_model", "internal"))
                if selected_model in EXTERNAL_LLM_MODELS:
                    try:
                        assistant.set_llm_model(selected_model)
                        assistant.set_llm_mode("always")
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
