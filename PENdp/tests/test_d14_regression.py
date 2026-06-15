#!/usr/bin/env python3
"""
PENdp D14 Regression Test — 28 test points across 3 P0 fixes

Tests:
  Fix 1: Merged pipelines (orchestrator → integration)
  Fix 2: D14_WEIGHT single source of truth
  Fix 3: Weight adjustment mechanism (patch_engine_weights deprecated)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = 0
FAIL = 0

def check(condition: bool, msg: str):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ [{PASS:2d}] {msg}")
    else:
        FAIL += 1
        print(f"  ❌ [{PASS+FAIL:2d}] {msg}")


def test_001_config_d14_weight_exists():
    """Fix 2: D14_WEIGHT constant in config.py"""
    from pendp.config import D14_WEIGHT
    check(D14_WEIGHT == 0.05, "D14_WEIGHT = 0.05 in config.py")


def test_002_config_d14_in_scoring_dimensions():
    """Fix 2: D14 dimension in SCORING_DIMENSIONS"""
    from pendp.config import SCORING_DIMENSIONS, D14_WEIGHT
    check("D14" in SCORING_DIMENSIONS, "D14 in SCORING_DIMENSIONS")
    check(SCORING_DIMENSIONS["D14"]["weight"] == D14_WEIGHT,
          f"SCORING_DIMENSIONS[D14].weight == {D14_WEIGHT}")
    check(SCORING_DIMENSIONS["D14"]["name"] == "深度学习置信度",
          "D14 name = '深度学习置信度'")


def test_003_config_g9_gate_exists():
    """Fix 2: G9 gate for D14 in GATE_CONFIG"""
    from pendp.config import GATE_CONFIG
    check("G9" in GATE_CONFIG, "G9 gate in GATE_CONFIG")
    check(GATE_CONFIG["G9"]["dim"] == "D14", "G9 dimension = D14")


def test_004_d14_integration_imports_weight():
    """Fix 2: d14_integration.py imports D14_WEIGHT from config"""
    from pendp.pipeline.d14_integration import D14_WEIGHT
    from pendp.config import D14_WEIGHT as CONFIG_WEIGHT
    check(D14_WEIGHT == CONFIG_WEIGHT,
          "d14_integration.D14_WEIGHT == config.D14_WEIGHT")


def test_005_af3_runner_imports_weight():
    """Fix 2: af3_runner.py imports D14_WEIGHT from config"""
    from pendp.pipeline.af3_runner import D14_WEIGHT
    from pendp.config import D14_WEIGHT as CONFIG_WEIGHT
    check(D14_WEIGHT == CONFIG_WEIGHT,
          "af3_runner.D14_WEIGHT == config.D14_WEIGHT")


def test_006_af3_runner_uses_weight():
    """Fix 2: AF3Runner.d14_weight = D14_WEIGHT"""
    from pendp.pipeline.af3_runner import AF3Runner
    runner = AF3Runner()
    check(runner.d14_weight == 0.05, "AF3Runner.d14_weight = 0.05")


def test_007_single_source_of_truth():
    """Fix 2: All three files reference same D14_WEIGHT value"""
    import pendp.config
    import pendp.pipeline.d14_integration
    import pendp.pipeline.af3_runner
    all_same = (
        pendp.config.D14_WEIGHT ==
        pendp.pipeline.d14_integration.D14_WEIGHT ==
        pendp.pipeline.af3_runner.D14_WEIGHT == 0.05
    )
    check(all_same, "All 3 files reference same D14_WEIGHT = 0.05")


def test_008_patch_engine_weights_deprecated():
    """Fix 3: patch_engine_weights is deprecated"""
    from pendp.pipeline.d14_integration import patch_engine_weights
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = patch_engine_weights()
        check(len(w) > 0 and issubclass(w[0].category, DeprecationWarning),
              "patch_engine_weights() raises DeprecationWarning")
        check(abs(sum(result.values()) - 1.0) < 0.01,
              "patch_engine_weights() result sums to ~1.0")
        check("D14" in result,
              "patch_engine_weights() result includes D14")


def test_009_update_weights_with_d14_exists():
    """Fix 3: update_weights_with_d14 exists in integration"""
    from pendp.pipeline.integration import update_weights_with_d14
    check(callable(update_weights_with_d14),
          "update_weights_with_d14 is callable")


def test_010_update_weights_sums_to_one():
    """Fix 3: update_weights_with_d14 output sums to 1.0"""
    from pendp.pipeline.integration import update_weights_with_d14
    for score in [2.0, 5.0, 8.0, 10.0]:
        w = update_weights_with_d14(d14_score=score)
        total = sum(w.values())
        check(abs(total - 1.0) < 0.01,
              f"update_weights_with_d14(score={score}): sum={total:.4f} ≈ 1.0")
        check("D14" in w, f"D14 in weights (score={score})")


def test_011_update_weights_d14_increases_with_score():
    """Fix 3: D14 weight increases with D14 score"""
    from pendp.pipeline.integration import update_weights_with_d14
    w_low = update_weights_with_d14(d14_score=2.0)
    w_high = update_weights_with_d14(d14_score=9.0)
    check(w_high["D14"] > w_low["D14"],
          f"D14 weight: {w_low['D14']}(score=2) → {w_high['D14']}(score=9)")


def test_012_neutral_score_no_change():
    """Fix 3: Score 5.0 produces D14 weight close to base"""
    from pendp.pipeline.integration import update_weights_with_d14
    w = update_weights_with_d14(d14_score=5.0)
    check(abs(w["D14"] - 0.05) < 0.01,
          f"D14 weight at score 5.0 = {w['D14']} ≈ 0.05")


def test_013_engine_has_d14_function():
    """Fix 2: D14 scoring function in engine.py"""
    from pendp.scoring.engine import DIMENSION_FUNCTIONS, score_dl_confidence
    check("D14" in DIMENSION_FUNCTIONS, "D14 in DIMENSION_FUNCTIONS")
    check(callable(DIMENSION_FUNCTIONS["D14"]),
          "D14 scoring function is callable")
    check(callable(score_dl_confidence),
          "score_dl_confidence is callable")


def test_014_d14_scores_well():
    """Fix 2: score_dl_confidence returns valid scores"""
    from pendp.scoring.engine import score_dl_confidence
    test_cases = [
        ("CRGDKGPDC", 6.0, 9.0),   # Cyclic, good length
        ("AAAA", 4.0, 8.0),        # Short, no structure
        ("MRWQEMGYIFYPRKLR", 4.0, 9.0),  # Long
    ]
    for seq, lo, hi in test_cases:
        score = score_dl_confidence(seq)
        check(lo <= score <= hi,
              f"D14 score for {seq}: {score} ∈ [{lo}, {hi}]")


def test_015_orchestrator_stages_replaced():
    """Fix 1: Orchestrator stages 2-4 no longer stub"""
    from pendp.pipeline.orchestrator import PipelineOrchestrator
    import inspect
    s2_src = inspect.getsource(PipelineOrchestrator.stage2_docking)
    s3_src = inspect.getsource(PipelineOrchestrator.stage3_md)
    s4_src = inspect.getsource(PipelineOrchestrator.stage4_qsar)
    check("integration" in s2_src and "STUB" not in s2_src,
          "Stage 2 uses integration, not stub")
    check("integration" in s3_src and "STUB" not in s3_src,
          "Stage 3 uses integration, not stub")
    check("integration" in s4_src and "STUB" not in s4_src,
          "Stage 4 uses integration, not stub")


def test_016_integration_pipeline_exists():
    """Fix 1: integration module exists with run_full_pipeline"""
    from pendp.pipeline.integration import run_full_pipeline
    check(callable(run_full_pipeline),
          "integration.run_full_pipeline is callable")


def test_017_integration_skip_md():
    """Fix 1: integration pipeline with skip_md=True"""
    from pendp.pipeline.integration import run_full_pipeline
    candidates = [{"sequence": "CRGDKGPDC"}, {"sequence": "RWKFGGFK"}]
    results = run_full_pipeline(candidates, skip_md=True, verbose=False)
    check(len(results) <= len(candidates),
          f"skip_md pipeline: {len(results)} results")
    if results:
        check("d14_score" in results[0],
              "Results contain d14_score")
        check("qsar_score" in results[0],
              "Results contain qsar_score")


def test_018_integration_full():
    """Fix 1: integration pipeline with MD enabled"""
    from pendp.pipeline.integration import run_full_pipeline
    candidates = [{"sequence": "CRGDKGPDC"}, {"sequence": "RWKFGGFK"}]
    results = run_full_pipeline(candidates, skip_md=False, verbose=False)
    check(len(results) <= len(candidates),
          f"full pipeline: {len(results)} results")
    if results:
        check("md_stability" in results[0],
              "Results contain md_stability (from MD stage)")
        check("md_pass" in results[0] or "md_stability" in results[0],
              "Results contain MD stability info")


def test_019_integration_reintegrate_scores():
    """Fix 1: D14-weighted re-scoring works"""
    from pendp.pipeline.integration import _reintegrate_scores
    candidates = [{
        "sequence": "CRGDKGPDC",
        "d14_score": 7.0,
        "qsar_score": 8.0,
    }]
    results = _reintegrate_scores(candidates)
    check(len(results) == 1, "1 candidate processed")
    check("total_score" in results[0], "total_score present")
    check("d14_score" in results[0], "d14_score present")
    check("weights_used" in results[0], "weights_used present")


def test_020_full_pipeline_stage_count():
    """Fix 1: Full pipeline returns 5 stages"""
    from pendp.pipeline.orchestrator import PipelineOrchestrator
    orch = PipelineOrchestrator()
    seqs = ["CRGDKGPDC", "KPSSPPEE", "AAAA", "RWKFGGFK"]
    result = orch.run_full_pipeline(seqs, verbose=False)
    check(len(result.stages) == 5, f"5 stages in pipeline")
    stage_names = [s.name for s in result.stages]
    check(stage_names == ['ML广筛', '分子对接', 'MD验证', 'QSAR精修', '湿实验闭环'],
          f"Stage names: {stage_names}")
    check(result.status == "completed", f"Pipeline status = completed")


def test_021_orchestrator_stage_results_format():
    """Fix 1: StageResult format preserved"""
    from pendp.pipeline.orchestrator import PipelineOrchestrator, StageResult
    orch = PipelineOrchestrator()
    seqs = ["CRGDKGPDC", "RWKFGGFK"]
    result = orch.run_full_pipeline(seqs, verbose=False)
    for s in result.stages:
        check(isinstance(s, StageResult), f"{s.name} is StageResult")
        check(hasattr(s, "stage"), f"{s.name}.stage exists")
        check(hasattr(s, "n_input"), f"{s.name}.n_input exists")
        check(hasattr(s, "n_output"), f"{s.name}.n_output exists")
        check(hasattr(s, "candidates"), f"{s.name}.candidates exists")


def test_022_d14_integrated_scoring():
    """Fix 3: run_d14_integrated_scoring works"""
    from pendp.pipeline.integration import run_d14_integrated_scoring
    candidates = [{"sequence": "CRGDKGPDC"}, {"sequence": "AAAA"}]
    results = run_d14_integrated_scoring(candidates, verbose=False)
    check(len(results) == 2, "2 results from D14 scoring")
    for r in results:
        check("d14_score" in r, "d14_score in result")
        check("d14_weighted" in r, "d14_weighted flag in result")


def test_023_af3_runner_predict():
    """Fix 2: AF3Runner.predict_structure returns D14 info"""
    from pendp.pipeline.af3_runner import AF3Runner
    runner = AF3Runner()
    result = runner.predict_structure("CRGDKGPDC")
    check("d14_score" in result, "predict contains d14_score")
    check("d14_weight" in result, "predict contains d14_weight")
    check("adjusted_weights" in result, "predict contains adjusted_weights")
    check("confidence" in result, "predict contains confidence")
    check(result["d14_weight"] == 0.05, "d14_weight = 0.05")


def test_024_d14_integration_patch_forwards():
    """Fix 3: patch_engine_weights forwards to update_weights_with_d14"""
    from pendp.pipeline.d14_integration import patch_engine_weights
    from pendp.pipeline.integration import update_weights_with_d14
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        patch_result = patch_engine_weights()
        direct_result = update_weights_with_d14(d14_score=5.0)
    # Should produce same-or-similar results for neutral score
    check(abs(patch_result.get("D14", 0) - direct_result.get("D14", 0)) < 0.02,
          "patch_engine_weights forwards to update_weights_with_d14")


def test_025_scoring_engine_includes_d14():
    """Fix 2: ScoringEngine scores include D14"""
    from pendp.scoring.engine import ScoringEngine
    engine = ScoringEngine()
    result = engine.score_sequence("CRGDKGPDC")
    check("D14" in result["dimensions"],
          "D14 dimension in score results")
    dim = result["dimensions"]["D14"]
    check(dim["weight"] == "5%",
          f"D14 weight = {dim['weight']}")
    check(4.0 <= dim["score"] <= 9.0,
          f"D14 score in valid range: {dim['score']}")


def test_026_source_imports_stable():
    """Fix 2: All module imports work"""
    try:
        import pendp.config
        import pendp.pipeline.integration
        import pendp.pipeline.d14_integration
        import pendp.pipeline.af3_runner
        from pendp.scoring.engine import score_dl_confidence
        check(True, "All module imports successful")
    except ImportError as e:
        check(False, f"Import error: {e}")


def test_027_weight_mutation_immutability():
    """Fix 3: update_weights_with_d14 doesn't mutate input"""
    from pendp.pipeline.integration import update_weights_with_d14
    base = {"D1": 0.25, "D2": 0.18, "D14": 0.05}
    original = dict(base)
    result = update_weights_with_d14(base_weights=base, d14_score=8.0)
    check(base == original, "Input weights not mutated by function")


def test_028_total_weight_always_one():
    """Fix 3: All weight configurations sum to 1.0"""
    from pendp.pipeline.integration import update_weights_with_d14
    all_ok = True
    for score in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        w = update_weights_with_d14(d14_score=float(score))
        total = sum(w.values())
        if abs(total - 1.0) > 0.02:
            all_ok = False
            break
    check(all_ok, "All D14 scores produce weights summing to 1.0")


# ── Run all tests ──
if __name__ == "__main__":
    tests = [
        ("D14_WEIGHT in config.py", test_001_config_d14_weight_exists),
        ("D14 in SCORING_DIMENSIONS", test_002_config_d14_in_scoring_dimensions),
        ("G9 gate for D14", test_003_config_g9_gate_exists),
        ("d14_integration imports D14_WEIGHT", test_004_d14_integration_imports_weight),
        ("af3_runner imports D14_WEIGHT", test_005_af3_runner_imports_weight),
        ("AF3Runner uses D14_WEIGHT", test_006_af3_runner_uses_weight),
        ("Single source of truth", test_007_single_source_of_truth),
        ("patch_engine_weights deprecated", test_008_patch_engine_weights_deprecated),
        ("update_weights_with_d14 exists", test_009_update_weights_with_d14_exists),
        ("update_weights sums to 1.0", test_010_update_weights_sums_to_one),
        ("D14 weight increases with score", test_011_update_weights_d14_increases_with_score),
        ("Neutral score no change", test_012_neutral_score_no_change),
        ("D14 function in engine", test_013_engine_has_d14_function),
        ("D14 scores valid", test_014_d14_scores_well),
        ("Stages 2-4 not stub", test_015_orchestrator_stages_replaced),
        ("integration.run_full_pipeline exists", test_016_integration_pipeline_exists),
        ("Integration skip_md works", test_017_integration_skip_md),
        ("Integration full works", test_018_integration_full),
        ("Reintegrate scores works", test_019_integration_reintegrate_scores),
        ("Full pipeline 5 stages", test_020_full_pipeline_stage_count),
        ("StageResult format preserved", test_021_orchestrator_stage_results_format),
        ("run_d14_integrated_scoring", test_022_d14_integrated_scoring),
        ("AF3Runner predict", test_023_af3_runner_predict),
        ("patch_engine forwards", test_024_d14_integration_patch_forwards),
        ("Scoring engine D14", test_025_scoring_engine_includes_d14),
        ("Module imports stable", test_026_source_imports_stable),
        ("Weight mutation immutable", test_027_weight_mutation_immutability),
        ("Total weight = 1.0", test_028_total_weight_always_one),
    ]

    print("=" * 60)
    print("PENdp D14 Regression Test — 28 test points")
    print("=" * 60)

    for name, func in tests:
        print(f"\n📋 {name}")
        try:
            func()
        except Exception as e:
            FAIL += 1
            print(f"  ❌ [{PASS+FAIL:2d}] EXCEPTION: {e}")

    print(f"\n{'='*60}")
    print(f"结果: {PASS}/{PASS+FAIL} 通过  ({FAIL} 失败)")
    if FAIL == 0:
        print("🎉 全部通过!")
    else:
        print(f"❌ {FAIL} 个测试失败")
    print(f"{'='*60}")

    sys.exit(0 if FAIL == 0 else 1)
