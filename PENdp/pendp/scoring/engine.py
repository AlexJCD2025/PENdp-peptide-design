"""
PENdp 7-Dimension Scoring Engine v2.0

Scoring formula:
  Total = 得点 × 10   (满分100)
  得点 = Σ(维度i分值 × 权重i)

Dimensions:
  D1 靶向基序(25%)  D2 物化性质(20%)  D3 积雪草酸协同(5%)
  D4 蛋白冠+LNP(30%) D5 Off-target(10%) D6 合成可行性(5%)
  D7 ESM相似度(5%)
"""
from typing import List, Optional, Dict, Tuple
import math


# ── Dimension scoring functions (each returns 0-10 scale) ──

def score_target_motif(seq: str, target_hint: str = "") -> float:
    """D1: 靶向基序评分 (25% weight).

    Scores based on known target motifs:
    - RGD → αvβ3 (highest for lung/tumor)
    - NGR → CD13
    - CendR motif (R/KXXR/K) → NRP-1
    - AKPC/A6 → p32
    - YHWY... → EGFR
    - KFGGFK → CD206
    """
    seq_upper = seq.upper()
    score = 5.0  # baseline

    # RGD motif (αvβ3/β5)
    if "RGD" in seq_upper:
        if "CRGD" in seq_upper or "CRGDK" in seq_upper:  # cyclic RGD
            score = 9.5
        else:
            score = 8.5
    # NGR motif (CD13)
    elif "NGR" in seq_upper:
        if "CRNGR" in seq_upper:  # cyclic NGR (iNGR)
            score = 9.0
        else:
            score = 8.0
    # CendR motif (R/KXXR/K at C-terminus)
    elif is_cendr_motif(seq_upper):
        score = 8.0
    # EGFR binding GE11
    elif "YHWY" in seq_upper:
        score = 8.0
    # p32 binding (AKPC or A6 pattern)
    elif seq_upper in ("KPSSPPEE", "AKPC"):
        score = 6.0
    # CD206 (RP-832c)
    elif "KFGGFK" in seq_upper:
        score = 8.0
    # CREKA (fibrin)
    elif seq_upper == "CREKA":
        score = 7.0
    # Minimal motif
    elif "R" in seq_upper and "K" in seq_upper:
        score = 6.5

    # Adjust for target hint
    if target_hint:
        hint_lower = target_hint.lower()
        if "nrp" in hint_lower or "cendr" in hint_lower:
            if is_cendr_motif(seq_upper):
                score = min(score + 1.0, 10.0)
        if "egfr" in hint_lower and "YHWY" in seq_upper:
            score = max(score, 8.5)
        if "cd206" in hint_lower and "KFGGFK" in seq_upper:
            score = max(score, 8.5)

    return round(min(score, 10.0), 1)


def is_cendr_motif(seq: str) -> bool:
    """Check for CendR motif: R/K at C-terminus with upstream basic residue."""
    cendr_patterns = ["RPAR", "KPAR", "RXXR", "KXXR"]
    for pattern in cendr_patterns:
        if pattern in seq:
            return True
    # Terminal check: last 3-4 residues end with R/K
    if len(seq) >= 3:
        tail = seq[-3:]
        if tail[0] in "RK" and tail[-1] in "RK":
            return True
    return False


def score_physiochem(seq: str) -> float:
    """D2: 物化性质评分 (20% weight).

    Checks: MW ≤ 5000, pI 5-11, GRAVY 0-3, charge balance.
    """
    seq_upper = seq.upper()
    n = len(seq_upper)
    if n == 0:
        return 0.0  # Empty sequence

    mw = calc_molecular_weight(seq_upper)

    score = 7.0  # baseline

    # Molecular weight check (target < 5000 Da)
    if mw > 5000:
        return 3.0  # Too large, penalty
    elif mw > 3000:
        score -= 1.0
    elif mw < 600:
        score += 1.0  # Very small peptides are good

    # Amino acid composition
    hydrophobic = sum(1 for aa in seq_upper if aa in "AVILMFWY")
    charged = sum(1 for aa in seq_upper if aa in "RKDE")
    polar = sum(1 for aa in seq_upper if aa in "NQSTCH")

    # Too hydrophobic = poor solubility
    if hydrophobic > n * 0.6:
        score -= 2.0
    # Too charged
    if charged > n * 0.5:
        score -= 1.0
    # Good balance
    if 0.2 < hydrophobic / n < 0.5 and charged > 1:
        score += 1.0

    # Cysteine count (disulfide = stability)
    cys_count = seq_upper.count("C")
    if 2 <= cys_count <= 4:
        score += 0.5  # Disulfide-stabilized

    # GRAVY approximation (hydrophobicity)
    gravy_approx = hydrophobic / n if n > 0 else 0
    if 0.1 <= gravy_approx <= 0.5:
        score += 0.5  # Sweet spot for membrane interaction

    return round(min(max(score, 0), 10.0), 1)


def calc_molecular_weight(seq: str, cyclic: bool = False,
                          amidated: bool = False,
                          acetylated: bool = False) -> float:
    """Calculate approximate molecular weight of a peptide sequence (Da).

    Args:
        seq: Amino acid sequence
        cyclic: If True, subtract 2 Da for disulfide bond
        amidated: If True, C-terminal amidation (-OH→-NH₂, -16 Da)
        acetylated: If True, N-terminal acetylation (+42 Da)
    """
    aa_weights = {
        'A': 89.1, 'R': 174.2, 'N': 132.1, 'D': 133.1, 'C': 121.2,
        'Q': 146.2, 'E': 147.1, 'G': 75.1, 'H': 155.2, 'I': 131.2,
        'L': 131.2, 'K': 146.2, 'M': 149.2, 'F': 165.2, 'P': 115.1,
        'S': 105.1, 'T': 119.1, 'W': 204.2, 'Y': 181.2, 'V': 117.2,
    }
    weight = sum(aa_weights.get(aa, 110.0) for aa in seq)
    # Subtract water for peptide bonds
    if len(seq) > 1:
        weight -= (len(seq) - 1) * 18.0
    # Disulfide bond (loss of 2H)
    if cyclic:
        weight -= 2.0
    # C-terminal amidation
    if amidated:
        weight -= 16.0  # -OH (17) + NH₂ (16) vs -OH (17), net -1... 
        # Actually: -COOH → -CONH₂ swaps -OH for -NH₂, difference = -16
    # N-terminal acetylation  
    if acetylated:
        weight += 42.0  # +COCH₃
    return round(weight, 1)


def score_asiatic_synergy(seq: str) -> float:
    """D3: 积雪草酸协同评分 (5% weight).

    How well does this peptide synergize with AA-LNP?
    - Membrane-active residues enhance AA's fusogenic effect
    - Amphipathic helices
    """
    seq_upper = seq.upper()
    score = 5.0  # baseline

    # Amphipathic helix potential (G, A, L, K rich)
    amphipathic = sum(1 for aa in seq_upper if aa in "GALK")
    if amphipathic >= 4:
        score += 2.0
    if amphipathic >= 6:
        score += 1.0

    # Arg/Lys content (cell-penetrating synergy)
    rk_count = seq_upper.count("R") + seq_upper.count("K")
    if rk_count >= 3:
        score += 2.0
    elif rk_count >= 2:
        score += 1.0

    # Cationic residues help with endosomal escape
    cationic = seq_upper.count("R") + seq_upper.count("K") + seq_upper.count("H")
    if cationic >= 4:
        score += 1.0

    # Disulfide-constrained peptides (cyclic) show better stability with LNP
    if seq_upper.startswith("C") and seq_upper.endswith("C"):
        score += 1.0

    return round(min(score, 10.0), 1)


def score_corona_lnp(seq: str) -> float:
    """D4: 蛋白冠+LNP兼容评分 (30% weight).

    - Serum protein adsorption potential (Arg/Lys rich)
    - Amphipathic balance
    - Lipid interaction potential
    - Cyclization helps LNP surface display
    """
    seq_upper = seq.upper()
    n = len(seq_upper) if seq_upper else 1
    score = 5.0

    # Arg/Lys promote protein corona formation
    rk = seq_upper.count("R") + seq_upper.count("K")
    rk_ratio = rk / n
    if rk_ratio > 0.3:
        score += 2.0
    elif rk_ratio > 0.2:
        score += 1.0

    # Amphipathic balance (hydrophobic vs hydrophilic)
    hydrophobic = sum(1 for aa in seq_upper if aa in "AVILMFWY")
    h_ratio = hydrophobic / n
    if 0.25 <= h_ratio <= 0.45:  # Sweet spot
        score += 2.0
    elif 0.15 <= h_ratio <= 0.55:
        score += 1.0
    else:
        score -= 1.0

    # Glycine/proline for flexibility (better LNP surface display)
    gp = seq_upper.count("G") + seq_upper.count("P")
    if gp >= 2:
        score += 1.0

    # Cyclized = better LNP surface display
    if seq_upper.startswith("C") and seq_upper.endswith("C"):
        score += 0.5

    # Rich in aromatic residues (π-π stacking with LNP lipids)
    aromatic = sum(1 for aa in seq_upper if aa in "FWY")
    if aromatic >= 2:
        score += 0.5

    return round(min(max(score, 0), 10.0), 1)


def score_off_target(seq: str) -> float:
    """D5: Off-target规避评分 (10% weight).

    Higher score = lower off-target risk.
    - Specific motif patterns
    - Avoid promiscuous sequences
    - Avoid overly short sequences that fit many receptors
    """
    seq_upper = seq.upper()
    n = len(seq_upper)
    score = 7.0

    # Very short sequences (<5aa) are more promiscuous
    if n < 5:
        score -= 1.5
    elif n < 7:
        score -= 0.5

    # Cyclic peptides have better specificity
    if seq_upper.startswith("C") and seq_upper.endswith("C"):
        score += 1.0

    # Too many Arg/Lys = polycationic, can bind anything
    rk = seq_upper.count("R") + seq_upper.count("K")
    if rk > n * 0.4:
        score -= 1.5
    elif rk > n * 0.3:
        score -= 0.5

    # Known specific motifs score bonus
    if "RGD" in seq_upper:
        score += 0.5
    if "NGR" in seq_upper:
        score += 0.5

    return round(min(max(score, 0), 10.0), 1)


def score_synthesis(seq: str) -> float:
    """D6: 合成可行性评分 (5% weight).

    - Shorter = easier
    - Fewer hydrophobic stretches = better yield
    - Cyclization adds complexity but manageable
    """
    seq_upper = seq.upper()
    n = len(seq_upper)
    score = 7.0

    # Length factor
    if n <= 5:
        score = 9.5
    elif n <= 8:
        score = 8.5
    elif n <= 12:
        score = 7.5
    elif n <= 15:
        score = 6.0
    else:
        score = 4.5

    # Long hydrophobic stretches (difficult synthesis)
    max_hydro_stretch = 0
    current_stretch = 0
    for aa in seq_upper:
        if aa in "AVILMFWY":
            current_stretch += 1
            max_hydro_stretch = max(max_hydro_stretch, current_stretch)
        else:
            current_stretch = 0
    if max_hydro_stretch > 4:
        score -= 1.0

    # Beta-sheet propensity (Y, V, I, F) → aggregation risk
    beta = sum(1 for aa in seq_upper if aa in "YVIFW")
    if beta > n * 0.4:
        score -= 1.0

    # Cyclization adds ~1 step but manageable
    if seq_upper.startswith("C") and seq_upper.endswith("C"):
        score -= 0.5  # Slight penalty but common

    return round(min(max(score, 0), 10.0), 1)


# ── Main scoring engine ──

DIMENSION_FUNCTIONS = {
    "D1": lambda seq: score_target_motif(seq),
    "D2": lambda seq: score_physiochem(seq),
    "D3": lambda seq: score_asiatic_synergy(seq),
    "D4": lambda seq: score_corona_lnp(seq),
    "D5": lambda seq: score_off_target(seq),
    "D6": lambda seq: score_synthesis(seq),
    "D9": lambda seq: score_conjugation_orientation(seq),
    "D14": lambda seq: score_dl_confidence(seq),
}


def score_dl_confidence(seq: str) -> float:
    """D14: Deep Learning / AlphaFold confidence proxy (5% weight).

    Scores sequence features correlated with structural prediction confidence:
    - Length suitable for AF3 prediction
    - Cyclization indicator
    - Glycine/proline content balance
    - Hydrophobic core potential
    - Charge distribution

    Added in PENdp P0: single source of truth for D14 scoring.
    """
    seq_upper = seq.upper()
    n = len(seq_upper)
    if n == 0:
        return 0.0

    score = 5.0  # Baseline

    # Length sweet spot for AF prediction
    if 10 <= n <= 30:
        score += 1.5
    elif n < 10:
        score += 0.5  # Short peptides are easy
    else:
        score -= 1.0  # Long peptides are hard for AF

    # Cyclization = better foldability
    if seq_upper.startswith("C") and seq_upper.endswith("C"):
        score += 1.5

    # Glycine content (too much = unstructured)
    glycine_count = seq_upper.count("G")
    gly_ratio = glycine_count / max(n, 1)
    if gly_ratio > 0.3:
        score -= 1.0
    elif gly_ratio < 0.1:
        score += 0.5

    # Proline content (too much = rigidity issues)
    pro_count = seq_upper.count("P")
    pro_ratio = pro_count / max(n, 1)
    if pro_ratio > 0.3:
        score -= 0.5

    # Hydrophobic residues signal structured core
    hydrophobic = sum(1 for aa in seq_upper if aa in "AVILMFWY")
    h_ratio = hydrophobic / max(n, 1)
    if 0.2 <= h_ratio <= 0.5:
        score += 1.0

    # Charged residue balance (well-folded proteins have balanced charge)
    charged = sum(1 for aa in seq_upper if aa in "RKDE")
    c_ratio = charged / max(n, 1)
    if 0.15 <= c_ratio <= 0.4:
        score += 0.5

    return round(min(max(score, 0), 10.0), 1)


def score_conjugation_orientation(seq: str) -> float:
    """D9: 偶联方向定向性评分 (suggested 5% for v2.1).

    Random vs oriented conjugation affects potency.
    Higher score = better for oriented LNP conjugation.

    Sources: ASSET Protocol (scFv定向), literature review.
    """
    seq_upper = seq.upper()
    n = len(seq_upper)
    if n == 0:
        return 0.0

    score = 5.0

    # C-terminal Cys = good for maleimide coupling
    if seq_upper.endswith("C"):
        score += 2.0

    # N-terminal Cys = also good
    if seq_upper.startswith("C"):
        score += 1.5

    # Both ends Cys = either orientation possible (but less specific)
    if seq_upper.startswith("C") and seq_upper.endswith("C"):
        score -= 0.5

    # Internal Lys = multiple conjugation sites (less specific)
    k_count = seq_upper.count("K")
    if k_count >= 2:
        score -= 1.0

    # Short sequences = easier to control orientation
    if n <= 6:
        score += 1.0

    # Disulfide-constrained = fixed orientation
    if seq_upper.startswith("C") and seq_upper.endswith("C"):
        score += 0.5

    return round(min(max(score, 0), 10.0), 1)

# ESMSimilarity needs ESM-2 embedding, separate
# D7 is handled by the pipeline if ESM model is loaded


class ScoringEngine:
    """PENdp 7-dimension scoring engine v2.0."""

    def __init__(self, esm_model=None):
        self.esm_model = esm_model  # Optional ESM-2 model for D7

    def score_sequence(self, seq: str, target_hint: str = "",
                       verbose: bool = False) -> Dict:
        """Score a single peptide sequence.

        Args:
            seq: Amino acid sequence
            target_hint: Optional target name for context-aware scoring
            verbose: Print dimension details

        Returns:
            dict with scores, total, and dimension breakdown
        """
        from pendp.config import SCORING_DIMENSIONS
        from pendp.scoring.gates import validate_sequence

        # Centralized validation: reject invalid input instead of scoring garbage.
        normalized, error = validate_sequence(seq)
        if error:
            return {
                "sequence": seq,
                "target_hint": target_hint,
                "total_score": 0.0,
                "meets_threshold": False,
                "recommendation": "invalid_sequence",
                "error": error,
                "dimensions": {},
            }
        seq = normalized

        scores = {}
        weights = {}
        for dim_id, dim_info in SCORING_DIMENSIONS.items():
            if dim_id == "D7":
                continue  # Handled separately if ESM available
            func = DIMENSION_FUNCTIONS.get(dim_id)
            if func:
                scores[dim_id] = func(seq)
                weights[dim_id] = dim_info["weight"]

        # D7: ESM similarity (use 5.0 as neutral if no model)
        if self.esm_model is not None:
            try:
                from pendp.esm.embeddings import calc_similarity_to_reference
                sim = calc_similarity_to_reference(
                    seq, self.esm_model, getattr(self, "esm_tokenizer", None))
                scores["D7"] = sim * 10.0  # Scale 0-1 to 0-10
            except Exception:
                scores["D7"] = 5.0
        else:
            scores["D7"] = 5.0
        weights["D7"] = SCORING_DIMENSIONS["D7"]["weight"]

        # Calculate total
        weighted_sum = sum(scores[d] * weights[d] for d in scores)
        total = round(weighted_sum * 10, 1)

        # Determine recommendation
        meets_threshold = total >= 65.0
        if total >= 80:
            recommendation = "strong_recommend"
        elif total >= 65:
            recommendation = "recommend"
        elif total >= 50:
            recommendation = "consider"
        else:
            recommendation = "not_recommend"

        result = {
            "sequence": seq,
            "target_hint": target_hint,
            "total_score": total,
            "meets_threshold": meets_threshold,
            "recommendation": recommendation,
            "dimensions": {},
        }
        for dim_id in sorted(scores.keys()):
            info = SCORING_DIMENSIONS.get(dim_id, {})
            result["dimensions"][dim_id] = {
                "name": info.get("name", dim_id),
                "weight": f"{info.get('weight', 0)*100:.0f}%",
                "score": scores[dim_id],
                "contribution": round(scores[dim_id] * info.get("weight", 0), 2),
            }

        if verbose:
            print(f"\n{'='*50}")
            print(f"PENdp Score: {seq}")
            print(f"{'='*50}")
            for dim_id, d in sorted(result["dimensions"].items()):
                bar = "█" * int(d["score"]) + "░" * (10 - int(d["score"]))
                print(f"  {dim_id} {d['name']:12s} [{d['weight']:>3s}]  "
                      f"{d['score']:4.1f}/10 {bar}")
            print(f"{'─'*50}")
            print(f"  TOTAL: {total}/100  "
                  f"{'✅ 合成可行' if meets_threshold else '❌ 低于阈值'}")

        return result

    def score_with_gates(self, seq: str, target_hint: str = "",
                         verbose: bool = False, log_json: bool = False) -> Dict:
        """Score a peptide and run through V3 gate pipeline.

        Returns the full scoring result PLUS gate evaluation.
        Gate FAIL on critical gates → eliminated regardless of total score.
        """
        # First, run standard scoring
        base_result = self.score_sequence(seq, target_hint, verbose=False)
        if "error" in base_result:
            return base_result  # Invalid sequence — skip gate evaluation

        # Extract dimension scores for gate evaluation
        dim_scores = {
            dim_id: base_result["dimensions"][dim_id]["score"]
            for dim_id in base_result["dimensions"]
        }

        # Run gate pipeline
        from pendp.scoring.gates import GatePipeline
        pipeline = GatePipeline(log_json=log_json)
        gate_result = pipeline.evaluate(dim_scores, seq)

        # Merge gate info into result
        gate_dict = {
            "overall_status": gate_result.overall_status,
            "eliminated": gate_result.eliminated,
            "elimination_reason": gate_result.elimination_reason if gate_result.eliminated else "",
            "can_proceed": gate_result.can_proceed,
            "pass_rate": round(gate_result.pass_rate * 100, 1),
            "gate_score": gate_result.gate_score,
            "critical_pass": gate_result.critical_pass_count,
            "cond_count": gate_result.cond_count,
            "gates": [],
        }
        for gr in gate_result.results:
            gate_dict["gates"].append({
                "gate_id": gr.gate.gate_id,
                "name": gr.gate.name,
                "criticality": gr.gate.criticality.value,
                "status": gr.status.value,
                "score": gr.score,
                "message": gr.message,
            })

        base_result["gate_pipeline"] = gate_dict

        # V4: Attach JSON log if requested
        if log_json:
            base_result["gate_pipeline"]["json_log"] = pipeline.flush_json()

        # Override recommendation if eliminated
        if gate_result.eliminated:
            base_result["recommendation"] = "gate_eliminated"
            base_result["meets_threshold"] = False

        if verbose:
            # Print standard scoring
            print(f"\n{'='*50}")
            print(f"PENdp V3 Score + Gates: {seq}")
            print(f"{'='*50}")
            for dim_id, d in sorted(base_result["dimensions"].items()):
                bar = "█" * int(d["score"]) + "░" * (10 - int(d["score"]))
                print(f"  {dim_id} {d['name']:12s} [{d['weight']:>3s}]  "
                      f"{d['score']:4.1f}/10 {bar}")
            print(f"{'─'*50}")
            print(f"  TOTAL: {base_result['total_score']}/100")

            # Print gate results
            print(pipeline.summary(gate_result))

        return base_result

    def score_multiple(self, sequences: List[str]) -> List[Dict]:
        """Score multiple sequences."""
        return [self.score_sequence(seq) for seq in sequences]

    def batch_gate_score(self, sequences: Dict[str, str],
                         log_json: bool = False) -> Dict:
        """V4: Batch score + gate + rank multiple peptides.

        Args:
            sequences: {name: seq} dict
            log_json: Enable JSON audit log

        Returns:
            Dict with ranked results, gate pipeline, and optional JSON log
        """
        from pendp.scoring.gates import GatePipeline
        pipeline = GatePipeline(log_json=log_json)
        ranked = pipeline.evaluate_batch(sequences, scoring_engine=self)

        results = []
        for name, gate_result, combined in ranked:
            sr = self.score_sequence(sequences[name])
            results.append({
                "name": name,
                "sequence": sequences[name],
                "total_score": sr["total_score"],
                "gate_status": gate_result.overall_status,
                "gate_score": gate_result.gate_score,
                "combined_score": combined,
                "eliminated": gate_result.eliminated,
                "can_proceed": gate_result.can_proceed,
            })

        return {
            "ranked": results,
            "pipeline": pipeline,
            "json_log": pipeline.flush_json() if log_json else "",
        }

    def batch_compare(self, seq_a: str, seq_b: str) -> Dict:
        """Compare two sequences dimension by dimension."""
        from pendp.config import SCORING_DIMENSIONS

        a = self.score_sequence(seq_a)
        b = self.score_sequence(seq_b)

        comparison = {
            "peptide_a": seq_a,
            "peptide_b": seq_b,
            "a_total": a["total_score"],
            "b_total": b["total_score"],
            "diff": round(a["total_score"] - b["total_score"], 1),
            "dimensions": {},
        }
        for dim_id in sorted(SCORING_DIMENSIONS.keys()):
            if dim_id in a["dimensions"] and dim_id in b["dimensions"]:
                d = SCORING_DIMENSIONS[dim_id]
                comparison["dimensions"][dim_id] = {
                    "name": d["name"],
                    "weight": d["weight"],
                    "a_score": a["dimensions"][dim_id]["score"],
                    "b_score": b["dimensions"][dim_id]["score"],
                }

        return comparison


    def curated_score(self, seq_or_name: str) -> Optional[Dict]:
        """Return curated reference score for known peptides.

        For peptides in the lung v6 database, returns the expert-curated
        score (e.g. iRGD=88.6). For unknown sequences, falls back to
        rule-based scoring.

        This is the 'reference score' vs 'computed score' distinction.
        """
        from pendp.database.sequences import PeptideDatabase
        db = PeptideDatabase()

        entry = db.get_by_sequence(seq_or_name)
        if not entry:
            entry = db.get_by_name(seq_or_name)

        if entry:
            return {
                "sequence": entry.sequence,
                "name": entry.name,
                "total_score": entry.score_total,
                "scores": entry.scores,
                "source": "curated_database",
                "target": entry.target,
                "meets_threshold": entry.meets_synthesis_threshold,
            }
        # Fallback to computed
        result = self.score_sequence(seq_or_name, verbose=False)
        result["source"] = "computed"
        return result


# ── Quick standalone scoring (no ESM needed) ──
def quick_score(seq: str, verbose: bool = True) -> Dict:
    """Quick score without ESM-2 model."""
    engine = ScoringEngine()
    return engine.score_sequence(seq, verbose=verbose)
