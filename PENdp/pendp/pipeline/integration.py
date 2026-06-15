"""
PENdp Integrated Pipeline: ESMFold → MD → QSAR → D14 → Scoring

Bridges computational biology modules into a unified scoring pipeline.
Supports both full and skip-MD modes for tiered screening.

Functions:
    run_full_pipeline(candidates, skip_md=False) — Full integrated pipeline
    update_weights_with_d14(dim_scores, d14_score) — Dynamic weight reallocation
"""
from typing import List, Dict, Optional, Tuple

from pendp.config import SCORING_DIMENSIONS, D14_WEIGHT


def update_weights_with_d14(
    base_weights: Optional[Dict[str, float]] = None,
    d14_score: float = 5.0,
) -> Dict[str, float]:
    """Dynamic weight adjustment factoring in D14 score.

    When D14 score is high (>6.0), D14 weight is increased by borrowing
    proportionally from all other dimensions. When low (<4.0), weight is
    reduced and redistributed. Total always sums to 1.0.

    Args:
        base_weights: Base dimension weights (default: from SCORING_DIMENSIONS)
        d14_score: D14 score (0-10 scale)

    Returns:
        Adjusted weights dict {dim_id: weight}, total = 1.0
    """
    if base_weights is None:
        base_weights = {
            dim_id: info["weight"]
            for dim_id, info in SCORING_DIMENSIONS.items()
        }

    weights = dict(base_weights)  # shallow copy
    base_d14 = weights.get("D14", D14_WEIGHT)

    # Map D14 score (0-10) to adjustment factor (0.5x to 1.5x)
    # Score 5.0 = no adjustment
    if d14_score >= 6.0:
        factor = 1.0 + (d14_score - 5.0) * 0.1  # Up to 1.5x at score 10
    elif d14_score <= 4.0:
        factor = 1.0 - (5.0 - d14_score) * 0.1  # Down to 0.5x at score 0
    else:
        factor = 1.0

    new_d14 = round(base_d14 * factor, 4)
    delta = new_d14 - base_d14

    # Borrow/redistribute delta proportionally from non-D14 dimensions
    other_dims = [k for k in weights if k != "D14"]
    other_total = sum(weights[k] for k in other_dims)
    if other_total > 0:
        for k in other_dims:
            weights[k] = round(weights[k] - delta * (weights[k] / other_total), 4)

    weights["D14"] = new_d14

    # Normalize to ensure total is exactly 1.0
    total = sum(weights.values())
    if abs(total - 1.0) > 0.001:
        weights = {k: round(v / total, 4) for k, v in weights.items()}

    return weights


# ── Pipeline stages ──


def _score_d14(seq: str) -> float:
    """Score D14: Deep Learning / AlphaFold confidence proxy.

    Returns a 0-10 score based on sequence features correlated with
    structural prediction confidence:
      - Length suitable for AF3 prediction (10-30 aa ideal)
      - Cyclization (disulfide) improves foldability
      - Low glycine content (unstructured penalty)
      - Hydrophobic core indicator
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
    gly_ratio = glycine_count / n
    if gly_ratio > 0.3:
        score -= 1.0
    elif gly_ratio < 0.1:
        score += 0.5

    # Proline content (too much = rigidity issues)
    pro_count = seq_upper.count("P")
    pro_ratio = pro_count / n
    if pro_ratio > 0.3:
        score -= 0.5

    # Hydrophobic residues signal structured core
    hydrophobic = sum(1 for aa in seq_upper if aa in "AVILMFWY")
    h_ratio = hydrophobic / n
    if 0.2 <= h_ratio <= 0.5:
        score += 1.0

    # Charged residue balance (well-folded proteins have balanced charge)
    charged = sum(1 for aa in seq_upper if aa in "RKDE")
    c_ratio = charged / n
    if 0.15 <= c_ratio <= 0.4:
        score += 0.5

    return round(min(max(score, 0), 10.0), 1)


def _esmfold_predict(seq: str) -> Dict:
    """Stage A: ESMFold prediction (simulated for now).

    In production, calls ESMFold API. Returns pLDDT scores and
    structural confidence metrics.
    """
    d14_score = _score_d14(seq)
    return {
        "sequence": seq,
        "plddt": round(5.0 + d14_score * 0.4, 1),  # Map 0-10 → 5-9
        "d14_score": d14_score,
        "confidence": "high" if d14_score >= 6.0 else "medium" if d14_score >= 4.0 else "low",
    }


def _md_simulation(candidates: List[Dict]) -> List[Dict]:
    """Stage B: MD simulation filter (simulated for now).

    In production, runs OpenMM/GROMACS. For now, filters based on
    sequence features correlated with MD stability.
    """
    filtered = []
    for c in candidates:
        seq = c["sequence"]
        seq_upper = seq.upper()
        n = len(seq_upper)

        # MD stability proxy score
        stability = 5.0

        # Cyclized peptides are more stable
        if seq_upper.startswith("C") and seq_upper.endswith("C"):
            stability += 2.0

        # Cysteine disulfide bridges
        cys_count = seq_upper.count("C")
        if cys_count >= 2:
            stability += 1.0

        # Too many Gly → flexible → unstable
        gly_ratio = seq_upper.count("G") / max(n, 1)
        if gly_ratio > 0.3:
            stability -= 1.0

        # Hydrophobic core
        hydrophobic = sum(1 for aa in seq_upper if aa in "AVILMFWY")
        h_ratio = hydrophobic / max(n, 1)
        if 0.15 <= h_ratio <= 0.5:
            stability += 1.0

        # Very short sequences are stable
        if n <= 6:
            stability += 1.0

        c["md_stability"] = round(min(max(stability, 0), 10.0), 1)
        c["md_pass"] = c["md_stability"] >= 4.0
        filtered.append(c)

    # Filter by stability, keep at least top half
    passed = [c for c in filtered if c.get("md_pass", False)]
    if not passed:
        # Fallback: take top scoring by stability
        filtered.sort(key=lambda x: x.get("md_stability", 0), reverse=True)
        passed = filtered[:max(1, len(filtered) // 2)]

    return passed


def _qsar_predict(candidates: List[Dict]) -> List[Dict]:
    """Stage C: QSAR/GNN refinement (simulated for now).

    In production, runs RDKit descriptors + XGBoost/GNN model.
    Adds qsar_score to each candidate.
    """
    for c in candidates:
        seq = c["sequence"]
        seq_upper = seq.upper()
        n = len(seq_upper)

        # QSAR proxy: simplified bioactivity prediction
        qsar = 5.0

        # Known functional motifs boost QSAR score
        if "RGD" in seq_upper:
            qsar += 2.0
        if "NGR" in seq_upper:
            qsar += 1.5
        if "YHWY" in seq_upper:
            qsar += 1.5
        if "KFGGFK" in seq_upper:
            qsar += 1.5

        # Cyclization improves bioactivity
        if seq_upper.startswith("C") and seq_upper.endswith("C"):
            qsar += 1.0

        # Optimal length for binding
        if 7 <= n <= 15:
            qsar += 1.0

        # Too many negative charges hurt cell penetration
        negative = seq_upper.count("D") + seq_upper.count("E")
        neg_ratio = negative / max(n, 1)
        if neg_ratio > 0.3:
            qsar -= 1.0

        # Arginine content (good for cell penetration)
        arg_count = seq_upper.count("R")
        if arg_count >= 2:
            qsar += 0.5

        # Aromatic residues for binding affinity
        aromatic = sum(1 for aa in seq_upper if aa in "FWY")
        if aromatic >= 2:
            qsar += 0.5

        c["qsar_score"] = round(min(max(qsar, 0), 10.0), 1)

    return candidates


def _reintegrate_scores(candidates: List[Dict]) -> List[Dict]:
    """Stage D: Re-score candidates combining all pipeline results.

    Uses dynamic weight adjustment (update_weights_with_d14) to
    recalculate total scores factoring in D14/ESMFold confidence.
    """
    from pendp.scoring.engine import ScoringEngine, DIMENSION_FUNCTIONS
    from pendp.config import SCORING_DIMENSIONS

    engine = ScoringEngine()

    for c in candidates:
        seq = c["sequence"]
        d14_score = c.get("d14_score", 5.0)

        # Get base dimension scores
        base_result = engine.score_sequence(seq, verbose=False)
        dim_scores = {
            dim_id: base_result["dimensions"][dim_id]["score"]
            for dim_id in base_result["dimensions"]
        }

        # Inject D14 score
        dim_scores["D14"] = d14_score

        # Dynamic weight adjustment
        weights = update_weights_with_d14(d14_score=d14_score)

        # Recalculate total
        weighted_sum = sum(
            dim_scores.get(d, 5.0) * weights.get(d, 0)
            for d in weights
        )
        total = round(weighted_sum * 10, 1)

        # Add QSAR boost if available
        qsar = c.get("qsar_score", 5.0)
        # QSAR contributes as a modifier to the total score
        qsar_boost = (qsar - 5.0) * 2  # ±10 points max
        total = round(total + qsar_boost, 1)

        c["total_score"] = total
        c["d14_score"] = d14_score
        c["weights_used"] = weights

        # Update recommendation
        if total >= 80:
            c["recommendation"] = "strong_recommend"
        elif total >= 65:
            c["recommendation"] = "recommend"
        elif total >= 50:
            c["recommendation"] = "consider"
        else:
            c["recommendation"] = "not_recommend"

    return candidates


def run_full_pipeline(
    candidates: List[Dict],
    skip_md: bool = False,
    verbose: bool = True,
) -> List[Dict]:
    """Run the full integrated pipeline on candidate peptides.

    Pipeline: ESMFold → (MD) → QSAR → D14 Scoring

    Args:
        candidates: List of candidate dicts with at least 'sequence' key
        skip_md: If True, skip MD simulation stage (fast screening mode)
        verbose: Print progress

    Returns:
        Updated candidates with pipeline scores, sorted by total_score desc
    """
    import time
    t0 = time.time()

    if verbose:
        print(f"\n{'='*50}")
        print(f"🔬 Integration Pipeline — {len(candidates)} candidates")
        print(f"{'='*50}")

    # Make working copies
    results = [dict(c) for c in candidates]

    # Stage A: ESMFold prediction
    if verbose:
        print(f"\n  Stage A: ESMFold prediction...")
    for i, c in enumerate(results):
        fold_result = _esmfold_predict(c["sequence"])
        c.update(fold_result)
        if verbose and (i + 1) % 10 == 0:
            print(f"    Progress: {i+1}/{len(results)}")

    # Stage B: MD simulation (optional)
    if not skip_md:
        if verbose:
            print(f"\n  Stage B: MD simulation filter...")
        results = _md_simulation(results)
        if verbose:
            print(f"    After MD: {len(results)} candidates")
    else:
        if verbose:
            print(f"\n  Stage B: MD simulation SKIPPED (skip_md=True)")

    # Stage C: QSAR prediction
    if verbose:
        print(f"\n  Stage C: QSAR/GNN refinement...")
    results = _qsar_predict(results)

    # Stage D: Re-integrate scores with D14 weighting
    if verbose:
        print(f"\n  Stage D: Re-scoring with D14 integration...")
    results = _reintegrate_scores(results)

    # Sort by total score descending
    results.sort(key=lambda x: x.get("total_score", 0), reverse=True)

    elapsed = time.time() - t0
    if verbose:
        print(f"\n  ✅ Pipeline complete — {len(results)} results")
        if results:
            print(f"  Top: {results[0]['sequence']} ({results[0]['total_score']}/100)")
        print(f"  ⏱  {elapsed:.1f}s")
        print(f"{'='*50}")

    return results


def run_d14_integrated_scoring(
    candidates: List[Dict],
    verbose: bool = False,
) -> List[Dict]:
    """Lightweight D14-integrated scoring without full pipeline.

    Faster path: just adds D14 scoring and dynamic weight adjustment
    to existing candidates without running ESMFold/MD/QSAR.
    """
    results = []
    for c in candidates:
        seq = c["sequence"]
        d14 = _score_d14(seq)
        weights = update_weights_with_d14(d14_score=d14)

        entry = dict(c)
        entry["d14_score"] = d14
        entry["weights_used"] = weights
        entry["d14_weighted"] = True
        results.append(entry)

    return results
