#!/usr/bin/env python3
"""
Tests for the scoring evaluation harness (ROADMAP Phase 0).

Uses SYNTHETIC outcomes (not real wet-lab data) to verify the plumbing:
loader round-trip, correlation math, direction handling, per-dimension
correlations, baseline, and the n<3 guard.
"""
import sys
import os
import csv
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = 0
FAIL = 0


def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {msg}")
    else:
        FAIL += 1
        print(f"  ❌ {msg}")


# A spread of real peptides so heuristic scores vary.
PANEL = ["CRGDKGPDC", "RWKFGGFK", "CNGRC", "CREKA", "KPSSPPEE",
         "RRRRRRRRRR", "AAAA", "YHWYGYTPQNVI"]


def _synthetic_records(direction="higher_better", noise=0.0):
    """Build records whose outcome is monotone in the heuristic score, so a
    correct harness must report a high positive Spearman."""
    from pendp.scoring.engine import ScoringEngine
    from pendp.eval import WetlabRecord
    engine = ScoringEngine()
    recs = []
    for i, seq in enumerate(PANEL):
        total = engine.score_sequence(seq)["total_score"]
        outcome = total + noise * ((-1) ** i)
        if direction == "lower_better":
            outcome = -outcome  # invert; effective_outcome should flip it back
        recs.append(WetlabRecord(sequence=seq, value=outcome, direction=direction,
                                 assay="synthetic", target="test"))
    return recs


def test_correlation_higher_better():
    print("\n📋 Spearman high when outcome tracks score (higher_better)")
    from pendp.eval import evaluate_scoring
    rep = evaluate_scoring(_synthetic_records("higher_better"))
    check(rep.n == len(PANEL), f"all {len(PANEL)} records used (n={rep.n})")
    check(rep.spearman > 0.9, f"Spearman ρ > 0.9 (got {rep.spearman:.3f})")


def test_direction_lower_better():
    print("\n📋 direction=lower_better flips outcome correctly")
    from pendp.eval import evaluate_scoring
    rep = evaluate_scoring(_synthetic_records("lower_better"))
    check(rep.spearman > 0.9,
          f"ρ still positive after lower_better flip (got {rep.spearman:.3f})")


def test_per_dimension_and_baseline():
    print("\n📋 Per-dimension + baseline populated")
    from pendp.eval import evaluate_scoring
    rep = evaluate_scoring(_synthetic_records("higher_better"))
    check(len(rep.per_dimension_spearman) >= 8, "per-dimension correlations present")
    check(not (rep.baseline_spearman != rep.baseline_spearman), "baseline ρ computed (not NaN)")
    check(rep.beats_baseline() in (True, False), "beats_baseline() returns a verdict")


def test_small_n_guard():
    print("\n📋 n<3 returns NaN with a note, no crash")
    from pendp.eval import evaluate_scoring, WetlabRecord
    rep = evaluate_scoring([WetlabRecord("CRGDKGPDC", 80.0)])
    check(rep.n == 1 and rep.spearman != rep.spearman, "n=1 → Spearman NaN")
    check("Need >= 3" in rep.note, "note explains the requirement")


def test_loader_roundtrip():
    print("\n📋 CSV loader round-trip")
    from pendp.eval import load_dataset, SCHEMA_COLUMNS
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as f:
        w = csv.writer(f)
        w.writerow(SCHEMA_COLUMNS)
        w.writerow(["CRGDKGPDC", "av-b3", "binding", "Kd", "12.5", "nM",
                    "lower_better", "3", "B1", "2026-06-01", "lab", "ok"])
        w.writerow(["", "", "", "", "", "", "", "", "", "", "", ""])  # skipped (no seq)
        w.writerow(["AAAA", "", "binding", "Kd", "not_a_number", "nM",
                    "lower_better", "1", "", "", "", ""])  # skipped (bad value)
        path = f.name
    recs = load_dataset(path)
    os.unlink(path)
    check(len(recs) == 1, f"only the valid row loaded (got {len(recs)})")
    check(recs[0].direction == "lower_better" and recs[0].value == 12.5, "fields parsed")
    check(recs[0].effective_outcome == -12.5, "lower_better effective_outcome negated")


def test_empty_dataset():
    print("\n📋 Missing dataset → empty list, no crash")
    from pendp.eval import load_dataset
    check(load_dataset("/nonexistent/path/xyz.csv") == [], "missing file returns []")


if __name__ == "__main__":
    print("=" * 50)
    print("PENdp eval harness tests (Phase 0)")
    print("=" * 50)

    test_correlation_higher_better()
    test_direction_lower_better()
    test_per_dimension_and_baseline()
    test_small_n_guard()
    test_loader_roundtrip()
    test_empty_dataset()

    print("\n" + "=" * 50)
    print(f"结果: {PASS}/{PASS + FAIL} 通过  ({FAIL} 失败)")
    if FAIL == 0:
        print("🎉 全部通过!")
    else:
        print("⚠️  有失败项")
        sys.exit(1)
    print("=" * 50)
