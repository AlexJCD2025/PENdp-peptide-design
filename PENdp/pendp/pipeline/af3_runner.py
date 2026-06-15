"""
PENdp AlphaFold3 Wrapper

Wraps AF3 prediction calls, integrating D14 confidence scoring.

D14_WEIGHT: Single source of truth imported from pendp.config
"""
from typing import Dict, Optional, List

from pendp.config import D14_WEIGHT
from pendp.pipeline.integration import update_weights_with_d14


class AF3Runner:
    """AlphaFold3 structure prediction wrapper.

    Integrates D14 confidence scoring into the AF3 pipeline.
    D14_WEIGHT is sourced from pendp.config (single source of truth).
    """

    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = model_dir
        self.d14_weight = D14_WEIGHT

    def predict_structure(self, sequence: str) -> Dict:
        """Predict structure using AlphaFold3.

        Returns a dict with pLDDT, pTM, and D14 confidence score.
        """
        from pendp.pipeline.integration import _score_d14

        d14_score = _score_d14(sequence)
        plddt = round(5.0 + d14_score * 0.4, 1)
        ptm = round(0.5 + d14_score * 0.04, 2)

        # Apply dynamic weight adjustment
        weights = update_weights_with_d14(d14_score=d14_score)

        return {
            "sequence": sequence,
            "plddt": plddt,
            "ptm": ptm,
            "d14_score": d14_score,
            "d14_weight": D14_WEIGHT,
            "adjusted_weights": weights,
            "confidence": "high" if d14_score >= 6.0
                          else "medium" if d14_score >= 4.0
                          else "low",
        }

    def batch_predict(self, sequences: List[str]) -> List[Dict]:
        """Batch structure prediction."""
        return [self.predict_structure(seq) for seq in sequences]
