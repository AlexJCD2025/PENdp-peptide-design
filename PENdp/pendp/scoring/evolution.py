"""
PENdp V4 Virtual Directed Evolution

PeptAI-inspired autonomous iteration: generate variants of a candidate
peptide, score them through the Gate Pipeline, and select top improvers.

No wet-lab required — pure computational evolution using:
- Single-point mutations (20 AA × sequence length)
- Gate Pipeline re-scoring
- Improvement ranking (gate_score + total_score)
- Multi-round iteration
"""
from typing import Dict, List, Tuple, Optional
import itertools

# Standard 20 amino acids
ALL_AA = list("ACDEFGHIKLMNPQRSTVWY")

# Conservative substitutions (BLOSUM-inspired)
CONSERVATIVE_SUBS = {
    'A': 'GS', 'C': 'S',  'D': 'EN', 'E': 'DQ', 'F': 'YW',
    'G': 'A',  'H': 'NY', 'I': 'LV', 'K': 'R',  'L': 'IV',
    'M': 'LI', 'N': 'DH', 'P': '',   'Q': 'E',  'R': 'K',
    'S': 'AT', 'T': 'S',  'V': 'IL', 'W': 'FY', 'Y': 'FW',
}

# Enhancing mutations for delivery system (targeted improvements)
ENHANCING_MUTATIONS = {
    # Add Cys for disulfide / conjugation
    "add_terminal_cys": "Append C to C-terminus for maleimide conjugation",
    "add_nterm_cys": "Prepend C to N-terminus",
    # Add Arg for endosomal escape
    "add_arg": "Add Arg at position for enhanced endosomal escape",
    # Add Gly/Pro for LNP flexibility
    "add_gly_pro": "Insert G or P for LNP surface display flexibility",
}


class DirectedEvolution:
    """Virtual directed evolution engine for PENdp."""

    def __init__(self, scoring_engine=None, gate_pipeline=None):
        from pendp.scoring.engine import ScoringEngine
        from pendp.scoring.gates import GatePipeline

        self.engine = scoring_engine or ScoringEngine()
        self.gates = gate_pipeline or GatePipeline()

    # ── Variant generation ──

    def generate_variants(self, seq: str, mode: str = "full",
                          max_variants: int = 500,
                          include_enhancing: bool = True) -> List[Tuple[str, str, str]]:
        """Generate variant sequences from a parent peptide.

        Args:
            seq: Parent peptide sequence
            mode: 'full' (all point mutations), 'conservative' (BLOSUM),
                  'enhancing' (targeted improvements only)
            max_variants: Cap on number of variants generated
            include_enhancing: Add enhancing mutations

        Returns:
            List of (variant_seq, mutation_description, mutation_type)
        """
        variants = []
        seq_upper = seq.upper()
        n = len(seq_upper)

        if mode in ("full", "conservative"):
            for pos in range(n):
                original = seq_upper[pos]
                candidates = (CONSERVATIVE_SUBS.get(original, ALL_AA)
                              if mode == "conservative" else ALL_AA)
                for new_aa in candidates:
                    if new_aa and new_aa != original:
                        variant = seq_upper[:pos] + new_aa + seq_upper[pos+1:]
                        desc = f"{original}{pos+1}{new_aa}"
                        variants.append((variant, desc, "point_mutation"))

        if include_enhancing:
            # C-terminal Cys addition
            if not seq_upper.endswith("C"):
                variants.append((seq_upper + "C", "+C(C-term)", "enhancing"))
            # N-terminal Cys (if doesn't start with C)
            if not seq_upper.startswith("C"):
                variants.append(("C" + seq_upper, "C+(N-term)", "enhancing"))
            # Terminal Cys for cyclization
            if not (seq_upper.startswith("C") and seq_upper.endswith("C")):
                variants.append(("C" + seq_upper + "C", "cyclic(C)", "enhancing"))

            # Add Arg at C-term for endosomal escape (if R/K count < 3)
            rk_count = sum(1 for aa in seq_upper if aa in "RK")
            if rk_count < 3:
                variants.append((seq_upper + "R", "+R(C-term)", "enhancing"))

            # Add Gly for flexibility
            if seq_upper.count("G") < 2:
                variants.append((seq_upper + "G", "+G(C-term)", "enhancing"))

        # Deduplicate and limit
        seen = set()
        unique = []
        for v, desc, vtype in variants:
            if v not in seen:
                seen.add(v)
                unique.append((v, desc, vtype))
        return unique[:max_variants]

    # ── Evolution round ──

    def evolve_round(self, seq: str, mode: str = "full",
                     top_k: int = 10, verbose: bool = False) -> Dict:
        """Run one round of directed evolution.

        Args:
            seq: Parent peptide sequence
            mode: Mutation mode ('full', 'conservative')
            top_k: Number of top variants to return
            verbose: Print progress

        Returns:
            Dict with parent info, top variants, and evolution summary
        """
        # Score parent
        parent_score = self.engine.score_sequence(seq)
        parent_dim = {dim_id: d["score"] for dim_id, d in parent_score["dimensions"].items()}
        parent_gate = self.gates.evaluate(parent_dim, seq)

        if verbose:
            print(f"\n🧬 Parent: {seq}")
            print(f"   Score={parent_score['total_score']:.1f} | Gate={parent_gate.overall_status} "
                  f"score={parent_gate.gate_score:.1f}")

        # Generate variants
        variants = self.generate_variants(seq, mode=mode)
        if verbose:
            print(f"   Generating {len(variants)} variants...")

        # Score all variants
        scored = []
        for variant_seq, desc, vtype in variants:
            vs = self.engine.score_sequence(variant_seq)
            vd = {dim_id: d["score"] for dim_id, d in vs["dimensions"].items()}
            vg = self.gates.evaluate(vd, variant_seq)
            improvement = vg.gate_score - parent_gate.gate_score + (vs["total_score"] - parent_score["total_score"])
            scored.append({
                "sequence": variant_seq,
                "mutation": desc,
                "type": vtype,
                "total_score": vs["total_score"],
                "gate_status": vg.overall_status,
                "gate_score": vg.gate_score,
                "eliminated": vg.eliminated,
                "can_proceed": vg.can_proceed,
                "improvement": round(improvement, 1),
                "cond_count": vg.cond_count,
            })

        # Sort: not eliminated, best improvement first
        scored.sort(key=lambda x: (x["eliminated"], -x["gate_score"], -x["total_score"]))

        # Identify key improvements
        improvers = [s for s in scored if s["improvement"] > 0 and not s["eliminated"]]
        degenerate = [s for s in scored if s["improvement"] == 0 and not s["eliminated"]]
        worse = [s for s in scored if s["improvement"] < 0 or s["eliminated"]]

        if verbose:
            print(f"   ✓ Improved: {len(improvers)}  = Same: {len(degenerate)}  ✗ Worse: {len(worse)}")
            if improvers:
                print(f"\n   Top improvements:")
                for i, v in enumerate(improvers[:5]):
                    print(f"   {i+1}. {v['sequence']:15s} ({v['mutation']:12s})  "
                          f"Δ={v['improvement']:+5.1f}  Gate={v['gate_status']}")

        return {
            "parent": {
                "sequence": seq,
                "total_score": parent_score["total_score"],
                "gate_score": parent_gate.gate_score,
                "gate_status": parent_gate.overall_status,
            },
            "top_variants": scored[:top_k],
            "stats": {
                "total_variants": len(scored),
                "improved": len(improvers),
                "same": len(degenerate),
                "worse": len(worse),
                "best_improvement": improvers[0]["improvement"] if improvers else 0,
                "best_variant": improvers[0]["sequence"] if improvers else seq,
            },
            "all_variants": scored,  # For multi-round iteration
        }

    # ── Multi-round evolution ──

    def evolve(self, seq: str, rounds: int = 3, mode: str = "conservative",
               top_k: int = 5, verbose: bool = True) -> Dict:
        """Run multiple rounds of directed evolution.

        Each round: take top variant from previous round as new parent.
        """
        results = []
        current_seq = seq

        for r in range(rounds):
            if verbose:
                print(f"\n{'═'*50}")
                print(f"🧬 Round {r+1}/{rounds} — parent: {current_seq}")
                print(f"{'═'*50}")

            round_result = self.evolve_round(current_seq, mode=mode, top_k=top_k, verbose=verbose)
            results.append(round_result)

            # Take best improver as next parent
            best = round_result["stats"]["best_variant"]
            if best == current_seq:
                if verbose:
                    print(f"   ⏸ No improvement found — stopping evolution")
                break
            current_seq = best

        # Compile lineage
        lineage = [r["parent"]["sequence"] for r in results]
        if results[-1]["stats"]["best_variant"] != lineage[-1]:
            lineage.append(results[-1]["stats"]["best_variant"])

        return {
            "rounds": len(results),
            "lineage": lineage,
            "original": seq,
            "final": current_seq,
            "total_improvement": (
                results[-1]["stats"]["best_improvement"]
                if results else 0
            ),
            "round_results": results,
        }

    def evolution_summary(self, evolution_result: Dict) -> str:
        """Human-readable evolution summary."""
        lines = [
            f"\n{'═'*60}",
            f"🧬 Directed Evolution Summary",
            f"{'═'*60}",
            f"  Original: {evolution_result['original']}",
            f"  Rounds: {evolution_result['rounds']}",
            f"  Lineage: {' → '.join(evolution_result['lineage'])}",
            f"  Final: {evolution_result['final']}",
            f"  Total improvement: {evolution_result['total_improvement']:+5.1f}",
        ]

        for i, rr in enumerate(evolution_result["round_results"]):
            lines.append(f"\n  Round {i+1}:")
            p = rr["parent"]
            lines.append(f"    Parent: {p['sequence']} | score={p['total_score']:.1f} | gate={p['gate_score']:.1f}")
            lines.append(f"    Variants: {rr['stats']['total_variants']} → "
                         f"↑{rr['stats']['improved']} ={rr['stats']['same']} ↓{rr['stats']['worse']}")
            if rr["top_variants"]:
                best = rr["top_variants"][0]
                lines.append(f"    Best: {best['sequence']} ({best['mutation']}) "
                             f"Δ={best['improvement']:+5.1f}")

        lines.append(f"{'═'*60}")
        return "\n".join(lines)


# ── Quick API ──

def evolve_peptide(seq: str, rounds: int = 3) -> Dict:
    """One-shot directed evolution."""
    evolver = DirectedEvolution()
    return evolver.evolve(seq, rounds=rounds)
