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

# Scoring system v2.0
SCORING_DIMENSIONS = {
    "D1": {"name": "靶向基序",       "code": "target_motif",   "weight": 0.25, "col": 0},
    "D2": {"name": "物化性质",       "code": "physiochem",     "weight": 0.20, "col": 1},
    "D3": {"name": "积雪草酸协同",    "code": "asiatic_synergy","weight": 0.05, "col": 2},
    "D4": {"name": "蛋白冠+LNP兼容",  "code": "corona_lnp",    "weight": 0.30, "col": 3},
    "D5": {"name": "Off-target规避",  "code": "off_target",    "weight": 0.10, "col": 4},
    "D6": {"name": "合成可行性",      "code": "synthesis",     "weight": 0.05, "col": 5},
    "D7": {"name": "ESM相似度",       "code": "esm_similarity","weight": 0.05, "col": 6},
}

SYNTHESIS_THRESHOLD = 65  # 合成阈值：≥65分建议推进

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
