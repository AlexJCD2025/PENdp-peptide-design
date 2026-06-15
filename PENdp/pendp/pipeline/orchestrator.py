"""PENdp 五关融合漏斗 Pipeline Orchestrator

    第一关: ML广筛 (ESM-2 + CPP + 评分) → 1000+ 候选
    第二关: 分子对接 (integration管线, skip_md) → Top 50-100
    第三关: MD动力学验证 (integration管线, full) → Top 20-30
    第四关: QSAR/GNN精修 (integration管线, D14权重) → 5-10 最终候选
    第五关: 湿实验闭环 → 数据回流
"""
import time
from typing import List, Optional, Dict
from dataclasses import dataclass, field

from pendp.config import get_device
from pendp.scoring.engine import ScoringEngine
from pendp.cpp.classifier import CPPClassifier
from pendp.database.sequences import PeptideDatabase, PeptideEntry


@dataclass
class StageResult:
    """Result from a single pipeline stage."""
    stage: int
    name: str
    n_input: int
    n_output: int
    elapsed_seconds: float
    candidates: List[Dict] = field(default_factory=list)
    details: str = ""


@dataclass
class PipelineResult:
    """Complete pipeline result."""
    input_sequences: int
    stages: List[StageResult] = field(default_factory=list)
    final_candidates: List[Dict] = field(default_factory=list)
    total_elapsed: float = 0.0
    status: str = "completed"
    error: Optional[str] = None


class PipelineOrchestrator:
    """Orchestrate the full 5-stage fusion funnel."""

    def __init__(self):
        self.esm_model = None
        self.esm_tokenizer = None
        self.scoring_engine = ScoringEngine()
        self.cpp_classifier = CPPClassifier()
        self.db = PeptideDatabase()

    def load_esm(self, model_size: str = "150M"):
        """Load ESM-2 model (needed for Stage 1 ML screening)."""
        from pendp.esm.model import load_esm_model
        model, tokenizer, config = load_esm_model(model_size)
        self.esm_model = model
        self.esm_tokenizer = tokenizer
        self.scoring_engine.esm_model = model
        self.scoring_engine.esm_tokenizer = tokenizer
        return config

    # ── Stage 0: Decision Framework ──

    def stage0_decision(self, indication_hint: str = "",
                        verbose: bool = True) -> StageResult:
        """Stage 0: Disease-first decision framework.

        Before screening peptides, recommend the right indication
        and targeting strategy.
        """
        t0 = time.time()
        from pendp.decision.framework import (
            DecisionFramework, list_subsystems, pipeline_summary)

        decider = DecisionFramework()

        if indication_hint:
            assessment = decider.evaluate_indication(indication_hint)
            recommendation = assessment
        else:
            recommendation = {
                "message": "未指定适应症",
                "subsystems": list_subsystems(),
                "pipeline": pipeline_summary(),
                "suggestion": "建议先选适应症(推荐IPF)",
            }

        elapsed = time.time() - t0
        if verbose:
            print(f"\n{'='*60}")
            print(f"Stage 0: 决策框架")
            print(f"{'='*60}")
            if indication_hint:
                a = recommendation
                print(f"  适应症: {a['indication']}")
                print(f"  综合评分: {a['average_score']}/10")
                print(f"  决策: {a['decision']}")
                if a.get('recommendation'):
                    r = a['recommendation']
                    print(f"  策略: {r.targeting_strategy}")
                    print(f"  时间线: {r.timeline}")
            else:
                for s in recommendation["subsystems"][:3]:
                    print(f"  {s['organ']:10s} → {s['top_indication']}")
                r = recommendation["pipeline"][0]
                print(f"\n  推荐: {r['indication']} ({r['strategy']})")
            print(f"  耗时: {elapsed:.1f}s")

        return StageResult(
            stage=0, name="决策框架", n_input=1, n_output=1,
            elapsed_seconds=round(elapsed, 1),
            candidates=[recommendation],
            details=f"决策建议: {recommendation.get('decision', '选择适应症')}"
        )

    # ── Stage 1: ML Broad Screening ──

    def stage1_ml_screen(self, sequences: List[str],
                         verbose: bool = True) -> StageResult:
        """Stage 1: ESM-2 embedding + scoring → rank candidates.

        Args:
            sequences: List of peptide sequences to screen
            verbose: Print progress

        Returns:
            StageResult with scored and ranked candidates.
        """
        t0 = time.time()
        n_in = len(sequences)
        candidates = []

        if verbose:
            print(f"\n{'='*60}")
            print(f"Stage 1: ML 广筛 — {n_in} 条候选序列")
            print(f"{'='*60}")

        for i, seq in enumerate(sequences):
            score = self.scoring_engine.score_sequence(seq, verbose=False)

            # CPP prediction
            cpp = self.cpp_classifier.predict(seq)

            entry = {
                "sequence": seq,
                "total_score": score["total_score"],
                "recommendation": score["recommendation"],
                "cpp_probability": cpp["cpp_probability"],
                "is_cpp": cpp["is_cpp"],
                "dimensions": score["dimensions"],
            }
            candidates.append(entry)

            if verbose and (i + 1) % 10 == 0:
                print(f"  进度: {i+1}/{n_in}")

        # Sort by score descending
        candidates.sort(key=lambda x: x["total_score"], reverse=True)

        # Filter: score >= 65 threshold
        qualified = [c for c in candidates if c["total_score"] >= 65.0]

        elapsed = time.time() - t0

        if verbose:
            print(f"\n├─ 合格: {len(qualified)}/{n_in} (≥65分阈值)")
            print(f"├─ Top 5: {[c['sequence'] + '(' + str(c['total_score']) + ')' for c in qualified[:5]]}")
            print(f"└─ 耗时: {elapsed:.1f}s")

        return StageResult(
            stage=1, name="ML广筛", n_input=n_in, n_output=len(qualified),
            elapsed_seconds=round(elapsed, 1), candidates=qualified,
            details=f"ESM-2评分 + CPP分类: {len(qualified)}/{n_in}合格"
        )

    # ── Stage 2: Docking (integration pipeline, skip MD) ──

    def stage2_docking(self, candidates: List[Dict],
                       verbose: bool = True) -> StageResult:
        """Stage 2: Molecular docking via integration pipeline (skip MD).

        Runs integration pipeline with skip_md=True for fast coarse screening.
        Returns top candidates by re-scored total.
        """
        t0 = time.time()
        n_in = len(candidates)

        from pendp.pipeline.integration import run_full_pipeline

        # Run integration pipeline, skip MD for speed
        results = run_full_pipeline(candidates, skip_md=True, verbose=False)
        n_out = min(50, len(results))

        top = results[:n_out]

        elapsed = time.time() - t0
        if verbose:
            print(f"\nStage 2: 分子对接 (integration) — {n_in}→{n_out}")
            print(f"  管线: ESMFold + QSAR + D14 评分")
            if top:
                print(f"  Top: {top[0]['sequence']} ({top[0]['total_score']}/100)")

        return StageResult(
            stage=2, name="分子对接", n_input=n_in, n_output=n_out,
            elapsed_seconds=round(elapsed, 1), candidates=top,
            details=f"integration管线(skip_md): {n_out}/{n_in}通过"
        )

    # ── Stage 3: MD Filter (integration pipeline, full) ──

    def stage3_md(self, candidates: List[Dict],
                  verbose: bool = True) -> StageResult:
        """Stage 3: Molecular dynamics via integration pipeline (full).

        Runs integration pipeline with MD enabled.
        Returns candidates filtered by MD stability.
        """
        t0 = time.time()
        n_in = len(candidates)

        from pendp.pipeline.integration import run_full_pipeline

        # Run full integration pipeline with MD
        results = run_full_pipeline(candidates, skip_md=False, verbose=False)
        n_out = min(20, len(results))

        top = results[:n_out]

        elapsed = time.time() - t0
        if verbose:
            print(f"\nStage 3: MD动力学 (integration) — {n_in}→{n_out}")
            print(f"  管线: ESMFold + MD + QSAR + D14 评分")
            if top:
                print(f"  Top: {top[0]['sequence']} ({top[0]['total_score']}/100)")

        return StageResult(
            stage=3, name="MD验证", n_input=n_in, n_output=n_out,
            elapsed_seconds=round(elapsed, 1), candidates=top,
            details=f"integration管线(full): {n_out}/{n_in}通过"
        )

    # ── Stage 4: QSAR (integration pipeline, final ranking) ──

    def stage4_qsar(self, candidates: List[Dict],
                    verbose: bool = True) -> StageResult:
        """Stage 4: QSAR/GNN refinement via integration pipeline.

        Uses integration pipeline's QSAR results for final ranking.
        Returns top 5-10 candidates with D14-weighted scores.
        """
        t0 = time.time()
        n_in = len(candidates)

        from pendp.pipeline.integration import run_full_pipeline

        # Run full integration pipeline (already has QSAR from stage 3)
        results = run_full_pipeline(candidates, skip_md=False, verbose=False)
        n_out = min(10, max(5, len(results) // 2))

        top = results[:n_out]

        elapsed = time.time() - t0
        if verbose:
            print(f"\nStage 4: QSAR精修 (integration) — {n_in}→{n_out}")
            print(f"  管线: ESMFold + QSAR + D14 评分重排")
            if top:
                print(f"  Top: {top[0]['sequence']} ({top[0]['total_score']}/100)")

        return StageResult(
            stage=4, name="QSAR精修", n_input=n_in, n_output=n_out,
            elapsed_seconds=round(elapsed, 1), candidates=top,
            details=f"integration管线 + D14权重: {n_out}/{n_in}最终候选"
        )

    # ── Stage 5: Wet Lab (stub) ──

    def stage5_wetlab(self, candidates: List[Dict],
                      verbose: bool = True) -> StageResult:
        """Stage 5: Wet lab data management.

        Tracks synthesis status and prepares data for model retraining.
        """
        t0 = time.time()
        n_in = len(candidates)

        # Mark all as "awaiting synthesis"
        for c in candidates:
            c["synthesis_status"] = "pending"
            c["wetlab_notes"] = ""

        elapsed = time.time() - t0
        if verbose:
            print(f"\nStage 5: 湿实验闭环 — {n_in} 条待合成")
            print(f"  建议: 优先合成 Top 3 → 活性测定 → 数据回流训练")

        return StageResult(
            stage=5, name="湿实验闭环", n_input=n_in, n_output=n_in,
            elapsed_seconds=round(elapsed, 1), candidates=candidates,
            details=f"{n_in}条待合成, 合成后数据回流可更新ML模型"
        )

    # ── Full pipeline ──

    def run_full_pipeline(self, sequences: List[str],
                          verbose: bool = True) -> PipelineResult:
        """Run all 5 stages of the fusion funnel."""
        t_total = time.time()
        stages = []

        try:
            # Stage 1
            s1 = self.stage1_ml_screen(sequences, verbose)
            stages.append(s1)
            if not s1.candidates:
                return PipelineResult(
                    input_sequences=len(sequences),
                    stages=stages,
                    final_candidates=[],
                    total_elapsed=time.time() - t_total,
                    status="no_candidates",
                )

            # Stage 2
            s2 = self.stage2_docking(s1.candidates, verbose)
            stages.append(s2)

            # Stage 3
            s3 = self.stage3_md(s2.candidates, verbose)
            stages.append(s3)

            # Stage 4
            s4 = self.stage4_qsar(s3.candidates, verbose)
            stages.append(s4)

            # Stage 5
            s5 = self.stage5_wetlab(s4.candidates, verbose)
            stages.append(s5)

            final = s5.candidates
            elapsed = time.time() - t_total

            if verbose:
                print(f"\n{'='*60}")
                print(f"🔬 PENdp 管线完成!")
                print(f"   输入: {len(sequences)} 条候选")
                print(f"   输出: {len(final)} 条最终候选")
                print(f"   耗时: {elapsed:.1f}s")
                print(f"   Top 3:")
                for i, c in enumerate(final[:3]):
                    print(f"     {i+1}. {c['sequence']} — {c['total_score']:.1f}分")
                    if 'is_cpp' in c:
                        print(f"        CPP: {c['cpp_probability']:.1%}")
                print(f"{'='*60}")

            return PipelineResult(
                input_sequences=len(sequences),
                stages=stages,
                final_candidates=final,
                total_elapsed=round(elapsed, 1),
                status="completed",
            )

        except Exception as e:
            import traceback
            error_msg = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
            print(f"❌ Pipeline error: {error_msg}")
            return PipelineResult(
                input_sequences=len(sequences),
                stages=stages,
                final_candidates=[],
                total_elapsed=time.time() - t_total,
                status="error",
                error=error_msg,
            )

    def run_quick_screen(self, sequences: List[str]) -> StageResult:
        """Quick screening (Stage 1 only)."""
        return self.stage1_ml_screen(sequences, verbose=True)

    def run_from_database(self, top_n: int = None) -> PipelineResult:
        """Run pipeline on the lung v6 database."""
        peptides = self.db.lung_v6
        if top_n:
            peptides = sorted(peptides, key=lambda p: p.score_total, reverse=True)[:top_n]
        sequences = [p.sequence for p in peptides]
        return self.run_full_pipeline(sequences, verbose=True)


# ── Quick CLI helper ──
def quick_pipeline(seqs: List[str], esm_size: str = "150M") -> PipelineResult:
    """Run pipeline with ESM-2 model loading."""
    orch = PipelineOrchestrator()
    orch.load_esm(esm_size)
    return orch.run_full_pipeline(seqs)
