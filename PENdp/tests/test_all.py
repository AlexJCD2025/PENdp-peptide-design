#!/usr/bin/env python3
"""
PENdp 快速验证脚本 — 测试核心功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_scoring():
    print("\n🧪 测试: 评分引擎")
    from pendp.scoring.engine import ScoringEngine, quick_score
    from pendp.database.sequences import PeptideDatabase

    # Quick score (without ESM, so D7=5.0 instead of full score)
    result = quick_score("CRGDKGPDC", verbose=True)
    assert result["total_score"] > 70, f"iRGD too low: {result['total_score']}"
    print(f"  ✅ iRGD score: {result['total_score']}/100")

    # RP-832c
    result = quick_score("RWKFGGFK", verbose=False)
    print(f"  ✅ RP-832c score: {result['total_score']}/100")
    assert 55 < result["total_score"] < 85, f"RP-832c off: {result['total_score']}"

    # Compare (iRGD should score higher than AAAA)
    engine = ScoringEngine()
    irgd = engine.score_sequence("CRGDKGPDC", verbose=False)
    aaaa = engine.score_sequence("AAAA", verbose=False)
    assert irgd["total_score"] > aaaa["total_score"], "iRGD should > AAAA"
    print(f"  ✅ Compare: iRGD({irgd['total_score']}) > AAAA({aaaa['total_score']})")

    # Database
    db = PeptideDatabase()
    print(f"  ✅ Database: {len(db.lung_v6)} peptides in lung v6")
    assert len(db.lung_v6) == 13, f"Expected 13, got {len(db.lung_v6)}"
    print(f"  ✅ Top 3: {[p.name for p in db.top_n(3)]}")

    print("  ✅ 评分引擎全部通过!")


def test_database():
    print("\n🧪 测试: 数据库管理")

    from pendp.database.sequences import PeptideDatabase
    db = PeptideDatabase()

    # Search
    results = db.search("RGD")
    assert len(results) >= 2, f"RGD search: {len(results)}"
    print(f"  ✅ Search 'RGD': {len(results)} results")

    # Get by name
    irgd = db.get_by_name("iRGD")
    assert irgd is not None and irgd.sequence == "CRGDKGPDC"
    print(f"  ✅ Get iRGD: {irgd.name} ({irgd.sequence})")

    # Priority
    by_pri = db.by_priority()
    print(f"  ✅ Priority: high={len(by_pri['high'])}, "
          f"med={len(by_pri['medium'])}, low={len(by_pri['low'])}")

    # Threshold
    qualified = db.meets_threshold()
    print(f"  ✅ Meet threshold (≥65): {len(qualified)}/{len(db.lung_v6)}")

    # Target KG
    from pendp.database.targets import TargetKnowledgeGraph
    kg = TargetKnowledgeGraph()
    s = kg.summary()
    print(f"  ✅ Target KG: {s['total_targets']} targets, {len(s['diseases'])} diseases")

    ipf_targets = kg.by_disease("IPF")
    print(f"  ✅ IPF targets: {[t.name for t in ipf_targets]}")

    ligands = kg.ligands_for_disease("NSCLC")
    print(f"  ✅ NSCLC ligands: {ligands}")

    print("  ✅ 数据库全部通过!")


def test_cpp():
    print("\n🧪 测试: CPP分类器")
    from pendp.cpp.classifier import CPPClassifier, quick_cpp_predict

    # Rule-based
    result = quick_cpp_predict("CRGDKGPDC")
    print(f"  ✅ iRGD CPP: {result['cpp_probability']:.1%} ({result['method']})")

    result = quick_cpp_predict("AAAA")
    print(f"  ✅ AAAA CPP: {result['cpp_probability']:.1%} ({result['method']})")

    assert quick_cpp_predict("RRRRRK")["is_cpp"], "Poly-Arg should be CPP"
    print(f"  ✅ CPP规则分类器通过!")


def test_pipeline():
    print("\n🧪 测试: 管线编排")
    from pendp.pipeline.orchestrator import PipelineOrchestrator

    orch = PipelineOrchestrator()

    # Quick screen
    seqs = ["CRGDKGPDC", "KPSSPPEE", "AAAA", "RWKFGGFK"]
    result = orch.run_quick_screen(seqs)
    assert result.n_output > 0, "No candidates from quick screen"
    print(f"  ✅ Quick screen: {result.n_input}→{result.n_output} candidates")
    print(f"  ✅ Top: {result.candidates[0]['sequence']} "
          f"({result.candidates[0]['total_score']}/100)")

    # Pipeline (full, with stubs)
    result = orch.run_full_pipeline(seqs)
    assert len(result.stages) == 5, f"Expected 5 stages, got {len(result.stages)}"
    print(f"  ✅ Full pipeline: {result.input_sequences}→{len(result.final_candidates)} final")
    print(f"  ✅ Stages: {[s.name for s in result.stages]}")

    print("  ✅ 管线编排全部通过!")


if __name__ == "__main__":
    print("=" * 50)
    print("PENdp 完整验证测试")
    print("=" * 50)

    test_database()
    test_cpp()
    test_scoring()
    test_pipeline()

    print("\n" + "=" * 50)
    print("🎉 全部测试通过!")
    print("=" * 50)
