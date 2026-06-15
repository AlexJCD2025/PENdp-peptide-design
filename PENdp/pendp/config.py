"""
PENdp Configuration Management
"""
import os
from pathlib import Path

# Project root: PENdp/ (config.py is in pendp/config.py, so 2 levels up)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# ESM-2 model config
ESM_MODELS = {
    "8M":   {"name": "facebook/esm2_t6_8M_UR50D",   "dim": 320,  "speed": "fastest"},
    "35M":  {"name": "facebook/esm2_t12_35M_UR50D",  "dim": 480,  "speed": "fast"},
    "150M": {"name": "facebook/esm2_t30_150M_UR50D",  "dim": 640,  "speed": "recommended"},
    "650M": {"name": "facebook/esm2_t33_650M_UR50D",  "dim": 1280, "speed": "most_accurate"},
}

DEFAULT_ESM = "150M"

# CPP classifier
CPP_MODEL_PATH = DATA_DIR / "cpp_classifier_esm650.pkl"
CPP_SCALER_PATH = DATA_DIR / "cpp_scaler_esm650.pkl"

# D14 weight: single source of truth
D14_WEIGHT = 0.05  # Borrowed from D2(2.5%) + D4(2.5%)

# Scoring system v2.0
SCORING_DIMENSIONS = {
    "D1": {"name": "靶向基序",       "code": "target_motif",   "weight": 0.25, "col": 0},
    "D2": {"name": "物化性质",       "code": "physiochem",     "weight": 0.18, "col": 1},  # V3: 20→18%
    "D3": {"name": "积雪草酸协同",    "code": "asiatic_synergy","weight": 0.07, "col": 2},  # V3: 5→7%
    "D4": {"name": "蛋白冠+LNP兼容",  "code": "corona_lnp",    "weight": 0.28, "col": 3},  # V3: 30→28%
    "D5": {"name": "Off-target规避",  "code": "off_target",    "weight": 0.10, "col": 4},
    "D6": {"name": "合成可行性",      "code": "synthesis",     "weight": 0.05, "col": 5},
    "D7": {"name": "ESM相似度",       "code": "esm_similarity","weight": 0.02, "col": 6},  # V3: 5→2%
    "D9": {"name": "偶联定向性",       "code": "conjugation",    "weight": 0.05, "col": 7},  # V3: 正式接入
    "D14": {"name": "深度学习置信度",  "code": "dl_confidence", "weight": D14_WEIGHT, "col": 8},  # P0: ESMFold/AF3 confidence
}

SYNTHESIS_THRESHOLD = 65  # 合成阈值：≥65分建议推进

# ── V3 Gate System (PeptAI-inspired) ──
# Gate criticalities and thresholds. Actual gate logic in scoring/gates.py
GATE_CONFIG = {
    "G1": {"dim": "D1", "criticality": "critical",    "pass": 6.0, "fail": 3.0},
    "G2": {"dim": "D2", "criticality": "critical",    "pass": 5.0, "fail": 3.0},
    "G3": {"dim": "D3", "criticality": "nice",        "pass": 5.0, "fail": 2.0},
    "G4": {"dim": "D4", "criticality": "critical",    "pass": 5.0, "fail": 3.0},
    "G5": {"dim": "D5", "criticality": "important",   "pass": 5.0, "fail": 3.0},
    "G6": {"dim": "D6", "criticality": "important",   "pass": 5.0, "fail": 3.0},
    "G7": {"dim": "D7", "criticality": "nice",        "pass": 5.0, "fail": 1.0},
    "G8": {"dim": "D9", "criticality": "nice",        "pass": 5.0, "fail": 2.0},
    "G9": {"dim": "D14", "criticality": "nice",       "pass": 5.0, "fail": 2.0},
}

# Database files (fallback: builtin data)
DATABASE_FILES = {
    "lung_v6": DATA_DIR / "lung_peptides_v6.csv",
    "multi_organ_v2": DATA_DIR / "multi_organ_v2.csv",
    "targets": DATA_DIR / "target_knowledge_graph.yaml",
}

# Device
def get_device():
    import torch
    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        return "cuda"
    return "cpu"
