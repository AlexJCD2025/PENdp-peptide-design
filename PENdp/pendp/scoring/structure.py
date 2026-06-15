"""
PENdp V4 Structure Analysis Module

Extracts structural features from peptide sequences without requiring
full 3D structure prediction. Uses:
- Sequence-based secondary structure propensity (Chou-Fasman style)
- ESM-2 embedding-derived features (if model loaded)
- Designed for future ESMFold/AlphaFold plug-in

For delivery system design, key structural questions:
- Helical content → membrane interaction / AA synergy
- Flexibility (Gly/Pro) → LNP surface display
- Disulfide constraints → conformational stability
- Charge surface → endosomal escape efficiency
"""
from typing import Dict, Optional, Tuple
import math


# ── Chou-Fasman propensity scores (simplified) ──
# Alpha-helix propensity (higher = more helix-forming)
HELIX_PROPENSITY = {
    'A': 1.42, 'C': 0.70, 'D': 1.01, 'E': 1.51, 'F': 1.13,
    'G': 0.57, 'H': 1.00, 'I': 1.08, 'K': 1.16, 'L': 1.21,
    'M': 1.45, 'N': 0.67, 'P': 0.57, 'Q': 1.11, 'R': 0.98,
    'S': 0.77, 'T': 0.83, 'V': 1.06, 'W': 1.08, 'Y': 0.69,
}

# Beta-sheet propensity
SHEET_PROPENSITY = {
    'A': 0.83, 'C': 1.19, 'D': 0.54, 'E': 0.37, 'F': 1.38,
    'G': 0.75, 'H': 0.87, 'I': 1.60, 'K': 0.74, 'L': 1.30,
    'M': 1.05, 'N': 0.89, 'P': 0.55, 'Q': 1.10, 'R': 0.93,
    'S': 0.75, 'T': 1.19, 'V': 1.70, 'W': 1.37, 'Y': 1.47,
}

# Turn propensity
TURN_PROPENSITY = {
    'A': 0.66, 'C': 1.19, 'D': 1.46, 'E': 0.74, 'F': 0.60,
    'G': 1.56, 'H': 0.95, 'I': 0.47, 'K': 1.01, 'L': 0.59,
    'M': 0.60, 'N': 1.56, 'P': 1.52, 'Q': 0.98, 'R': 0.95,
    'S': 1.43, 'T': 0.96, 'V': 0.50, 'W': 0.96, 'Y': 1.14,
}

# Flexibility scale (higher = more flexible)
FLEXIBILITY = {
    'G': 1.0, 'P': 0.8, 'S': 0.7, 'N': 0.6, 'D': 0.6,
    'T': 0.5, 'A': 0.4, 'Q': 0.4, 'E': 0.4, 'K': 0.4,
    'R': 0.4, 'H': 0.3, 'M': 0.3, 'C': 0.2, 'L': 0.2,
    'V': 0.2, 'I': 0.2, 'F': 0.1, 'Y': 0.1, 'W': 0.1,
}


class StructureAnalyzer:
    """Analyze peptide structural features from sequence alone."""

    def __init__(self, esm_model=None, esm_tokenizer=None):
        self.esm_model = esm_model
        self.esm_tokenizer = esm_tokenizer

    def analyze(self, seq: str) -> Dict:
        """Full structural analysis of a peptide sequence.

        Returns dict with:
            helix_score, sheet_score, turn_score, predicted_class,
            flexibility, disorder_score, rg_estimate,
            disulfide_bonds, charge_clusters
        """
        if not seq:
            return {"error": "Empty sequence"}

        seq_upper = seq.upper()
        n = len(seq_upper)

        # Secondary structure propensity
        helix = sum(HELIX_PROPENSITY.get(aa, 1.0) for aa in seq_upper) / n
        sheet = sum(SHEET_PROPENSITY.get(aa, 1.0) for aa in seq_upper) / n
        turn = sum(TURN_PROPENSITY.get(aa, 1.0) for aa in seq_upper) / n

        # Predicted dominant class
        if helix >= sheet and helix >= turn:
            pred_class = "alpha-helical"
        elif sheet >= helix and sheet >= turn:
            pred_class = "beta-sheet"
        else:
            pred_class = "turn/loop"

        # Flexibility
        flex = sum(FLEXIBILITY.get(aa, 0.3) for aa in seq_upper) / n

        # Disulfide bonds
        cys_count = seq_upper.count('C')
        disulfide = cys_count // 2 if cys_count >= 2 else 0

        # Charge clusters (consecutive charged residues)
        charge_clusters = self._find_charge_clusters(seq_upper)

        # Radius of gyration estimate (Flory scaling: Rg ≈ R0 * N^ν)
        # ν = 0.6 for denatured, 0.33 for compact
        rg_denatured = 1.93 * (n ** 0.6)
        rg_compact = 2.5 * (n ** 0.33) if disulfide >= 1 else rg_denatured

        # Disorder prediction (high Gly/Pro/charged + low hydrophobic)
        disorder_favoring = sum(1 for aa in 'GPSRKDENQ' if aa in seq_upper)
        disorder_score = disorder_favoring / n

        # Amphipathicity: alternating hydrophobic/hydrophilic pattern
        amphipathic_score = self._amphipathic_score(seq_upper)

        # ESM-derived features (if model loaded)
        esm_features = {}
        if self.esm_model is not None:
            esm_features = self._esm_features(seq_upper)

        return {
            "sequence": seq,
            "length": n,
            "helix_propensity": round(helix, 3),
            "sheet_propensity": round(sheet, 3),
            "turn_propensity": round(turn, 3),
            "predicted_class": pred_class,
            "flexibility": round(flex, 3),
            "disulfide_bonds": disulfide,
            "disorder_score": round(disorder_score, 3),
            "amphipathic_score": round(amphipathic_score, 3),
            "rg_denatured_est": round(rg_denatured, 1),
            "rg_compact_est": round(rg_compact, 1),
            "charge_clusters": charge_clusters,
            "esm_features": esm_features,
        }

    def _find_charge_clusters(self, seq: str) -> int:
        """Count consecutive charged residue runs (≥3)."""
        clusters = 0
        run = 0
        for aa in seq:
            if aa in 'RKDEH':
                run += 1
            else:
                if run >= 3:
                    clusters += 1
                run = 0
        if run >= 3:
            clusters += 1
        return clusters

    def _amphipathic_score(self, seq: str) -> float:
        """Score alternating hydrophobic/hydrophilic pattern (0-1)."""
        hydro = set('AVILMFWY')
        if len(seq) < 2:
            return 0.5
        alternations = 0
        for i in range(len(seq) - 1):
            a_hydro = seq[i] in hydro
            b_hydro = seq[i + 1] in hydro
            if a_hydro != b_hydro:
                alternations += 1
        return alternations / (len(seq) - 1)

    def _esm_features(self, seq: str) -> Dict:
        """Extract features from ESM-2 embedding."""
        try:
            from pendp.esm.embeddings import get_embedding
            emb = get_embedding(self.esm_model, self.esm_tokenizer, seq)
            # Per-position embedding variance (disorder proxy)
            pos_var = float(emb.var())
            # Embedding norm (compactness proxy)
            emb_norm = float((emb ** 2).sum().sqrt())
            return {
                "embedding_variance": round(pos_var, 4),
                "embedding_norm": round(emb_norm, 2),
            }
        except Exception:
            return {}

    def summary(self, result: Dict) -> str:
        """Human-readable structure analysis summary."""
        lines = [
            f"\n{'─'*50}",
            f"🔬 Structure Analysis: {result['sequence']}",
            f"{'─'*50}",
            f"  Length: {result['length']}aa | Class: {result['predicted_class']}",
            f"  Helix={result['helix_propensity']:.2f} Sheet={result['sheet_propensity']:.2f} Turn={result['turn_propensity']:.2f}",
            f"  Flexibility={result['flexibility']:.2f} | Disorder={result['disorder_score']:.2f}",
            f"  Amphipathic={result['amphipathic_score']:.2f} | Disulfide={result['disulfide_bonds']}",
            f"  Rg(denat)={result['rg_denatured_est']:.0f}Å | Rg(compact)={result['rg_compact_est']:.0f}Å",
            f"  Charge clusters: {result['charge_clusters']}",
        ]
        if result['esm_features']:
            lines.append(f"  ESM var={result['esm_features'].get('embedding_variance', 'N/A')} "
                         f"norm={result['esm_features'].get('embedding_norm', 'N/A')}")
        lines.append(f"{'─'*50}")
        return "\n".join(lines)


# ── Quick API ──

def analyze_structure(seq: str, esm_model=None, esm_tokenizer=None) -> Dict:
    """One-shot structure analysis."""
    analyzer = StructureAnalyzer(esm_model, esm_tokenizer)
    return analyzer.analyze(seq)


def structure_score(seq: str) -> float:
    """Derive a 0-10 structure quality score from sequence features.

    Factors: flexibility (good for LNP), moderate disorder,
    amphipathicity, disulfide stabilization.
    """
    if not seq or not seq.strip():
        return 0.0
    a = StructureAnalyzer().analyze(seq)
    if "error" in a:
        return 0.0
    score = 5.0

    # Flexibility bonus (0.3-0.6 is sweet spot for LNP display)
    if 0.3 <= a["flexibility"] <= 0.6:
        score += 1.5

    # Disulfide stabilization
    if a["disulfide_bonds"] >= 1:
        score += 1.5

    # Amphipathic is good for membrane interaction
    if a["amphipathic_score"] >= 0.4:
        score += 1.0

    # Moderate disorder (too ordered = rigid, too disordered = unstable)
    if 0.3 <= a["disorder_score"] <= 0.6:
        score += 1.0

    # Charge clusters help endosomal escape but too many = toxicity
    if a["charge_clusters"] == 0:
        score += 0.5  # no clusters = less off-target
    elif a["charge_clusters"] <= 2:
        score += 0.5  # moderate = good

    return round(min(score, 10.0), 1)
