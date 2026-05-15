"""
CPP (Cell-Penetrating Peptide) Classifier

Uses ESM-2 embeddings + Logistic Regression to predict CPP probability.
Can load pre-trained model or train on small datasets.

Reference: GraphCPP + local ESM-2 classifier (LOOCV Accuracy: 0.8571)
"""
import pickle
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple
from pendp.config import CPP_MODEL_PATH, CPP_SCALER_PATH


class CPPClassifier:
    """CPP classifier using ESM-2 embeddings + Logistic Regression."""

    def __init__(self, model_path: Optional[str] = None,
                 scaler_path: Optional[str] = None):
        self.model = None
        self.scaler = None
        self._load_model(model_path, scaler_path)

    def _load_model(self, model_path: Optional[str] = None,
                    scaler_path: Optional[str] = None):
        path = Path(model_path or CPP_MODEL_PATH)
        scaler_p = Path(scaler_path or CPP_SCALER_PATH)

        if path.exists():
            with open(path, "rb") as f:
                self.model = pickle.load(f)
        else:
            print(f"⚠️ CPP model not found: {path}")
            print(f"   Will use rule-based fallback prediction.")

        if scaler_p.exists():
            with open(scaler_p, "rb") as f:
                self.scaler = pickle.load(f)
        else:
            self.scaler = None

    def predict(self, sequence: str, esm_embedding: Optional[np.ndarray] = None
                ) -> dict:
        """Predict if sequence is a CPP.

        Args:
            sequence: Peptide amino acid sequence
            esm_embedding: Pre-computed ESM-2 embedding (if available)

        Returns:
            dict with cpp_probability, is_cpp, method
        """
        if self.model is not None and esm_embedding is not None:
            # ML-based prediction
            emb_scaled = esm_embedding.reshape(1, -1)
            if self.scaler is not None:
                emb_scaled = self.scaler.transform(emb_scaled)
            prob = float(self.model.predict_proba(emb_scaled)[0, 1])
            pred = bool(self.model.predict(emb_scaled)[0])
            return {
                "cpp_probability": round(prob, 4),
                "is_cpp": pred,
                "method": "ml_esm_lr",
            }
        else:
            # Rule-based fallback
            return self._rule_based_predict(sequence)

    def predict_batch(self, sequences: List[str],
                      embeddings: Optional[np.ndarray] = None
                      ) -> List[dict]:
        """Predict CPP for multiple sequences."""
        results = []
        for i, seq in enumerate(sequences):
            emb = embeddings[i] if embeddings is not None and i < len(embeddings) else None
            results.append(self.predict(seq, emb))
        return results

    def _rule_based_predict(self, seq: str) -> dict:
        """Rule-based CPP prediction fallback.

        CPPs tend to be:
        - Short (< 30 aa)
        - Cationic (Arg/Lys rich)
        - Amphipathic
        """
        seq_upper = seq.upper()
        n = len(seq_upper)

        if n == 0:
            return {"cpp_probability": 0.0, "is_cpp": False, "method": "rule"}

        # Features
        rk_count = seq_upper.count("R") + seq_upper.count("K")
        rk_ratio = rk_count / n

        hydrophobic = sum(1 for aa in "AVILMFWY" if aa in seq_upper)
        h_ratio = hydrophobic / n

        charged = seq_upper.count("R") + seq_upper.count("K") + \
                  seq_upper.count("D") + seq_upper.count("E")
        charge_ratio = charged / n

        # Scoring
        score = 0.0

        # Cationic (most important CPP feature)
        if rk_ratio > 0.5:
            score += 0.55  # Very cationic = clear CPP
        elif rk_ratio > 0.3:
            score += 0.4
        elif rk_ratio > 0.2:
            score += 0.25

        # Amphipathic balance
        if 0.25 <= h_ratio <= 0.5 and rk_count >= 2:
            score += 0.2

        # Length (CPPs are usually not too long)
        if 5 <= n <= 25:
            score += 0.1
        elif n > 30:
            score -= 0.1

        # Disulfide-constrained (common in targeted CPPs)
        if seq_upper.startswith("C") and seq_upper.endswith("C"):
            score += 0.1

        # Tryptophan (membrane interaction)
        if "W" in seq_upper:
            score += 0.05

        prob = min(max(score, 0.0), 1.0)
        return {
            "cpp_probability": round(prob, 4),
            "is_cpp": prob > 0.5,
            "method": "rule",
        }


def quick_cpp_predict(seq: str) -> dict:
    """Quick CPP prediction without model loading."""
    classifier = CPPClassifier(model_path=None)
    return classifier._rule_based_predict(seq)
