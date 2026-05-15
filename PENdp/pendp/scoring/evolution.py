"""
PENdp V4 Virtual Directed Evolution

PeptAI-inspired autonomous iteration: generate variants of a candidate
peptide, score them through the Gate Pipeline, and select top improvers.

No wet-lab required — pure computational evolution using:
- Single-point mutations (20 AA × sequence length)
- Gate Pipeline re-scoring
- Improvement ranking (sorted by improvement delta)
- Multi-round iteration with cumulative improvement tracking

V4 fix: sorts by improvement delta, total_improvement is cumulative,
enhancing variants prioritized ahead of point mutations, rounds=0 handled.
"""
from typing import Dict, List, Tuple, Optional

ALL_AA = list("ACDEFGHIKLMNPQRSTVWY")

CONSERVATIVE_SUBS = {
    'A': 'GS', 'C': 'S',  'D': 'EN', 'E': 'DQ', 'F': 'YW',
    'G': 'A',  'H': 'NY', 'I': 'LV', 'K': 'R',  'L': 'IV',
    'M': 'LI', 'N': 'DH', 'P': '',   'Q': 'E',  'R': 'K',
    'S': 'AT', 'T': 'S',  'V': 'IL', 'W': 'FY', 'Y': 'FW',
}


class DirectedEvolution:
    """Virtual directed evolution engine for PENdp."""

    def __init__(self, scoring_engine=None, gate_pipeline=None):
        from pendp.scoring.engine import ScoringEngine
        from pendp.scoring.gates import GatePipeline
        self.engine = scoring_engine or ScoringEngine()
        self.gates = gate_pipeline or GatePipeline()

    def generate_variants(self, seq: str, mode: str = "full",
                          max_variants: int = 500,
                          include_enhancing: bool = True) -> List[Tuple[str, str, str]]:
        """Generate variant sequences. Enhancing variants come FIRST to avoid
        being dropped by the cap (V4 fix: prioritized bucket order)."""
        seq_upper = seq.upper()
        n = len(seq_upper)

        # Bucket 1: Enhancing mutations (prioritized)
        enhancing = []
        if include_enhancing:
            if not seq_upper.endswith("C"):
                enhancing.append((seq_upper + "C", "+C(C-term)", "enhancing"))
            if not seq_upper.startswith("C"):
                enhancing.append(("C" + seq_upper, "C+(N-term)", "enhancing"))
            if not (seq_upper.startswith("C") and seq_upper.endswith("C")):
                enhancing.append(("C" + seq_upper + "C", "cyclic(C)", "enhancing"))
            rk_count = sum(1 for aa in seq_upper if aa in "RK")
            if rk_count < 3:
                enhancing.append((seq_upper + "R", "+R(C-term)", "enhancing"))
            if seq_upper.count("G") < 2:
                enhancing.append((seq_upper + "G", "+G(C-term)", "enhancing"))

        # Bucket 2: Point mutations (if mode allows)
        point_muts = []
        if mode in ("full", "conservative"):
            for pos in range(n):
                original = seq_upper[pos]
                candidates = (CONSERVATIVE_SUBS.get(original, ALL_AA)
                              if mode == "conservative" else ALL_AA)
                for new_aa in candidates:
                    if new_aa and new_aa != original:
                        variant = seq_upper[:pos] + new_aa + seq_upper[pos+1:]
                        desc = f"{original}{pos+1}{new_aa}"
                        point_muts.append((variant, desc, "point_mutation"))

        # Combine: enhancing first, then point mutations; deduplicate; cap
        seen = set()
        unique = []
        for v, desc, vtype in enhancing + point_muts:
            if v not in seen:
                seen.add(v)
                unique.append((v, desc, vtype))
                if len(unique) >= max_variants:
                    break
        return unique

    def evolve_round(self, seq: str, mode: str = "full",
                     top_k: int = 10, verbose: bool = False) -> Dict:
        parent_score = self.engine.score_sequence(seq)
        parent_dim = {dim_id: d["score"] for dim_id, d in parent_score["dimensions"].items()}
        parent_gate = self.gates.evaluate(parent_dim, seq)

        if verbose:
            print(f"\n🧬 Parent: {seq}")
            print(f"   Score={parent_score['total_score']:.1f} | Gate={parent_gate.overall_status} "
                  f"score={parent_gate.gate_score:.1f}")

        variants = self.generate_variants(seq, mode=mode)
        if verbose:
            print(f"   Generating {len(variants)} variants...")

        scored = []
        for variant_seq, desc, vtype in variants:
            vs = self.engine.score_sequence(variant_seq)
            vd = {dim_id: d["score"] for dim_id, d in vs["dimensions"].items()}
            vg = self.gates.evaluate(vd, variant_seq)
            improvement = vg.gate_score - parent_gate.gate_score + (vs["total_score"] - parent_score["total_score"])
            scored.append({
                "sequence": variant_seq, "mutation": desc, "type": vtype,
                "total_score": vs["total_score"], "gate_status": vg.overall_status,
                "gate_score": vg.gate_score, "eliminated": vg.eliminated,
                "can_proceed": vg.can_proceed, "improvement": round(improvement, 1),
                "cond_count": vg.cond_count,
            })

        # V4 fix: sort by improvement delta, not absolute score
        scored.sort(key=lambda x: (x["eliminated"], -x["improvement"]))

        improvers = [s for s in scored if s["improvement"] > 0 and not s["eliminated"]]
        degenerate = [s for s in scored if s["improvement"] == 0 and not s["eliminated"]]
        worse = [s for s in scored if s["improvement"] < 0 or s["eliminated"]]

        if verbose:
            print(f"   + Improved: {len(improvers)}  = Same: {len(degenerate)}  - Worse: {len(worse)}")
            if improvers:
                print(f"\n   Top improvements:")
                for i, v in enumerate(improvers[:5]):
                    print(f"   {i+1}. {v['sequence']:15s} ({v['mutation']:12s})  "
                          f"delta={v['improvement']:+5.1f}  Gate={v['gate_status']}")

        return {
            "parent": {"sequence": seq, "total_score": parent_score["total_score"],
                       "gate_score": parent_gate.gate_score, "gate_status": parent_gate.overall_status},
            "top_variants": scored[:top_k],
            "stats": {
                "total_variants": len(scored), "improved": len(improvers),
                "same": len(degenerate), "worse": len(worse),
                "best_improvement": improvers[0]["improvement"] if improvers else 0,
                "best_variant": improvers[0]["sequence"] if improvers else seq,
            },
            "all_variants": scored,
        }

    def evolve(self, seq: str, rounds: int = 3, mode: str = "conservative",
               top_k: int = 5, verbose: bool = True) -> Dict:
        """Multi-round evolution. total_improvement is cumulative vs original."""
        if rounds < 1:
            return {"rounds": 0, "lineage": [seq], "original": seq, "final": seq,
                    "total_improvement": 0, "round_results": []}

        from pendp.scoring.gates import GatePipeline
        orig_score = self.engine.score_sequence(seq)
        orig_dim = {dim_id: d["score"] for dim_id, d in orig_score["dimensions"].items()}
        orig_gate = GatePipeline().evaluate(orig_dim, seq)
        orig_combined = orig_gate.gate_score + orig_score["total_score"]

        results = []
        current_seq = seq

        for r in range(rounds):
            if verbose:
                print(f"\n{'='*50}")
                print(f"Round {r+1}/{rounds} - parent: {current_seq}")
                print(f"{'='*50}")
            rr = self.evolve_round(current_seq, mode=mode, top_k=top_k, verbose=verbose)
            results.append(rr)
            best = rr["stats"]["best_variant"]
            if best == current_seq:
                if verbose:
                    print(f"   No improvement found - stopping evolution")
                break
            current_seq = best

        lineage = [r["parent"]["sequence"] for r in results]
        if results and results[-1]["stats"]["best_variant"] != lineage[-1]:
            lineage.append(results[-1]["stats"]["best_variant"])

        # Cumulative improvement
        final_score = self.engine.score_sequence(current_seq)
        final_dim = {dim_id: d["score"] for dim_id, d in final_score["dimensions"].items()}
        final_gate = GatePipeline().evaluate(final_dim, current_seq)
        final_combined = final_gate.gate_score + final_score["total_score"]
        total_improvement = round(final_combined - orig_combined, 1)

        return {
            "rounds": len(results), "lineage": lineage,
            "original": seq, "final": current_seq,
            "total_improvement": total_improvement, "round_results": results,
        }

    def evolution_summary(self, evolution_result: Dict) -> str:
        lines = [
            f"\n{'='*60}",
            f"Directed Evolution Summary",
            f"{'='*60}",
            f"  Original: {evolution_result['original']}",
            f"  Rounds: {evolution_result['rounds']}",
            f"  Lineage: {' -> '.join(evolution_result['lineage'])}",
            f"  Final: {evolution_result['final']}",
            f"  Total improvement: {evolution_result['total_improvement']:+5.1f}",
        ]
        for i, rr in enumerate(evolution_result["round_results"]):
            lines.append(f"\n  Round {i+1}:")
            p = rr["parent"]
            lines.append(f"    Parent: {p['sequence']} | score={p['total_score']:.1f} | gate={p['gate_score']:.1f}")
            lines.append(f"    Variants: {rr['stats']['total_variants']} -> "
                         f"+{rr['stats']['improved']} ={rr['stats']['same']} -{rr['stats']['worse']}")
            if rr["top_variants"]:
                best = rr["top_variants"][0]
                lines.append(f"    Best: {best['sequence']} ({best['mutation']}) "
                             f"delta={best['improvement']:+5.1f}")
        lines.append(f"{'='*60}")
        return "\n".join(lines)


def evolve_peptide(seq: str, rounds: int = 3) -> Dict:
    return DirectedEvolution().evolve(seq, rounds=rounds)
