#!/usr/bin/env python3
"""
PENdp V4.4 fix regression tests.

Guards the bugs found and fixed during the V4.4 merge:
  1. Scoring weights sum to exactly 1.0 (was 1.05 → ~5% score inflation)
  2. score_sequence totals never exceed 100
  3. pendp.esm.model imports without torch installed (module-level
     @torch.no_grad() crash)
  4. D14 dimension + G9 gate are wired and score in range
  5. Empty / boundary sequences are handled, not crashed
"""
import sys
import os

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


def test_weight_conservation():
    print("\n📋 Weight conservation (sum == 1.0)")
    from pendp.config import SCORING_DIMENSIONS
    total = sum(d["weight"] for d in SCORING_DIMENSIONS.values())
    check(abs(total - 1.0) < 1e-9, f"SCORING_DIMENSIONS weights sum to 1.0 (got {total})")


def test_no_score_inflation():
    print("\n📋 No score inflation (total <= 100)")
    from pendp.scoring.engine import ScoringEngine
    engine = ScoringEngine()
    panel = ["CRGDKGPDC", "RWKFGGFK", "CNGRC", "CREKA", "KPSSPPEE",
             "RRRRRRRRRR", "WWWWWWWWWW", "CCCCCCCCCC"]
    worst = 0.0
    for seq in panel:
        t = engine.score_sequence(seq)["total_score"]
        worst = max(worst, t)
        check(t <= 100.0, f"{seq}: total {t} <= 100")
    print(f"     (panel max total = {worst})")


def test_esm_import_without_torch():
    print("\n📋 ESM model imports without torch")
    # Importing the module must not evaluate torch at module scope.
    import importlib
    try:
        importlib.import_module("pendp.esm.model")
        ok = True
    except NameError:
        ok = False
    check(ok, "import pendp.esm.model does not raise NameError (no module-level torch)")


def test_d14_dimension():
    print("\n📋 D14 dimension wired")
    from pendp.scoring.engine import ScoringEngine, DIMENSION_FUNCTIONS, score_dl_confidence
    check("D14" in DIMENSION_FUNCTIONS, "D14 in DIMENSION_FUNCTIONS")
    r = ScoringEngine().score_sequence("CRGDKGPDC")
    check("D14" in r["dimensions"], "D14 present in score result")
    check(0.0 <= r["dimensions"]["D14"]["score"] <= 10.0, "D14 score in [0, 10]")
    check(score_dl_confidence("") == 0.0, "score_dl_confidence('') == 0.0 (empty guard)")


def test_g9_gate():
    print("\n📋 G9 (D14) gate wired")
    from pendp.scoring.engine import ScoringEngine
    gp = ScoringEngine().score_with_gates("CRGDKGPDC")["gate_pipeline"]
    ids = [g["gate_id"] for g in gp["gates"]]
    check("G9" in ids, f"G9 present in gate pipeline (gates: {ids})")
    g9 = next(g for g in gp["gates"] if g["gate_id"] == "G9")
    check(g9["criticality"] == "nice", "G9 is NICE_TO_HAVE (won't eliminate)")
    check(0.0 <= g9["score"] <= 10.0, "G9 score in [0, 10]")


def test_boundary_sequences():
    print("\n📋 Boundary sequences handled")
    from pendp.scoring.structure import structure_score, StructureAnalyzer
    from pendp.scoring.engine import ScoringEngine
    check(structure_score("") == 0.0, "structure_score('') == 0.0")
    check("error" in StructureAnalyzer().analyze(""), "analyze('') returns error, not crash")
    long_seq = "ACDEFGHIKLMNPQRSTVWY" * 3  # 60-mer
    t = ScoringEngine().score_sequence(long_seq)["total_score"]
    check(0.0 <= t <= 100.0, f"60-mer scored in range ({t})")


def test_input_validation():
    print("\n📋 Invalid sequences rejected, not scored")
    from pendp.scoring.engine import ScoringEngine
    engine = ScoringEngine()
    r = engine.score_sequence("!!!!")
    check("error" in r, "invalid sequence returns error result")
    check(r["total_score"] == 0.0, "invalid sequence scores 0.0, not a plausible value")
    check(r["recommendation"] == "invalid_sequence", "recommendation = invalid_sequence")
    # lowercase is normalized, not rejected
    check("error" not in engine.score_sequence("crgdkgpdc"), "lowercase normalized (not rejected)")
    rg = engine.score_with_gates("12345")
    check("error" in rg, "score_with_gates short-circuits on invalid input")


def test_ci_pass_denominator():
    print("\n📋 Gate CI-PASS denominator counts only CI gates")
    from pendp.scoring.engine import ScoringEngine
    from pendp.scoring.gates import PENDP_GATES, GateCriticality
    ci = sum(1 for g in PENDP_GATES
             if g.criticality in (GateCriticality.CRITICAL, GateCriticality.IMPORTANT))
    status = ScoringEngine().score_with_gates("CRGDKGPDC")["gate_pipeline"]["overall_status"]
    check(f"/{ci} CI-PASS" in status, f"denominator is {ci} (CI gates), not total gates — got: {status}")


if __name__ == "__main__":
    print("=" * 50)
    print("PENdp V4.4 fix regression tests")
    print("=" * 50)

    test_weight_conservation()
    test_no_score_inflation()
    test_esm_import_without_torch()
    test_d14_dimension()
    test_g9_gate()
    test_boundary_sequences()
    test_input_validation()
    test_ci_pass_denominator()

    print("\n" + "=" * 50)
    print(f"结果: {PASS}/{PASS + FAIL} 通过  ({FAIL} 失败)")
    if FAIL == 0:
        print("🎉 全部通过!")
    else:
        print("⚠️  有失败项")
        sys.exit(1)
    print("=" * 50)
