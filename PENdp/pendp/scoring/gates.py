"""
PENdp V4 Gate Decision Engine

PeptAI-inspired sequential gate layer atop 8-dimension scoring.
V4 adds: G0 calibration, JSON logging, COND smart suggestions.

Each dimension becomes a gate with PASS/FAIL/COND decision.
Critical gate FAIL → candidate eliminated regardless of total score.

Gates are executed in order (G0→G1→G8→GFINAL).
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from copy import deepcopy
import json
import time
import statistics


class GateStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    COND = "COND"
    SKIP = "SKIP"


class GateCriticality(Enum):
    CRITICAL = "critical"
    IMPORTANT = "important"
    NICE_TO_HAVE = "nice"


# ── Reference peptides for G0 calibration ──
REFERENCE_PEPTIDES = {
    "iRGD":        "CRGDKGPDC",
    "iNGR":        "CNGRC",
    "KP-10":       "YNWNSFGLRF",
    "RP-832c":     "KFGGFKK",
    "CREKA":       "CREKA",
    "A6 (AKPC)":   "KPSSPPEE",
}

# Standard 20 amino acids for validation
VALID_AA = set("ACDEFGHIKLMNPQRSTVWY")


def validate_sequence(seq: str) -> Tuple[str, Optional[str]]:
    """Validate and normalize a peptide sequence.

    Returns (normalized_sequence, error_message).
    Error is None if valid.
    """
    if not seq or not seq.strip():
        return "", "Empty sequence"
    cleaned = seq.strip().upper()
    invalid = set(cleaned) - VALID_AA
    if invalid:
        return cleaned, f"Invalid amino acid(s): {', '.join(sorted(invalid))}"
    return cleaned, None


def count_aa(seq: str, aa_set: str) -> int:
    """Count how many residues in seq belong to aa_set (by position, not type)."""
    return sum(1 for aa in seq if aa in aa_set)


@dataclass
class GateDef:
    """Definition of a single gate."""
    gate_id: str
    name: str
    dimension: str
    criticality: GateCriticality
    pass_threshold: float
    fail_threshold: float
    description: str
    fail_message: str
    cond_suggestion: str = ""

    def decide(self, score: float) -> Tuple[GateStatus, str]:
        if score >= self.pass_threshold:
            return GateStatus.PASS, f"✅ {self.name}: {score:.1f}/10 ≥ {self.pass_threshold}"
        elif score < self.fail_threshold:
            return GateStatus.FAIL, f"❌ {self.name}: {score:.1f}/10 < {self.fail_threshold} — {self.fail_message}"
        else:
            hint = f" 💡 {self.cond_suggestion}" if self.cond_suggestion else ""
            return GateStatus.COND, f"⚠️ {self.name}: {score:.1f}/10 (threshold {self.pass_threshold}){hint}"


@dataclass
class GateResult:
    gate: GateDef
    status: GateStatus
    score: float
    message: str
    suggestion: str = ""
    timestamp: str = ""


@dataclass
class GatePipelineResult:
    sequence: str
    results: List[GateResult] = field(default_factory=list)
    eliminated: bool = False
    elimination_reason: str = ""
    critical_pass_count: int = 0      # only CRITICAL gates that PASSED
    important_pass_count: int = 0     # IMPORTANT gates that PASSED
    critical_fail_count: int = 0
    cond_count: int = 0
    total_configured_gates: int = 0   # total gates in the pipeline (fixed)
    calibration_baselines: Dict[str, Dict] = field(default_factory=dict)

    @property
    def total_gates(self) -> int:
        return len(self.results)

    @property
    def pass_rate(self) -> float:
        passed = sum(1 for r in self.results if r.status == GateStatus.PASS)
        return passed / max(self.total_gates, 1)

    @property
    def overall_status(self) -> str:
        if self.eliminated:
            return f"❌ ELIMINATED (at G{self.total_gates}/{self.total_configured_gates})"
        ci_pass = self.critical_pass_count + self.important_pass_count
        ci_total = self.total_configured_gates  # use configured not evaluated
        if self.cond_count > 0:
            return f"⚠️ CONDITIONAL ({ci_pass}/{ci_total} CI-PASS)"
        return f"✅ PASSED ({ci_pass}/{ci_total} CI-PASS)"

    @property
    def can_proceed(self) -> bool:
        if self.eliminated:
            return False
        ci_total = 5  # G1,G2,G4(CRITICAL) + G5,G6(IMPORTANT) = 5
        ci_pass = self.critical_pass_count + self.important_pass_count
        if ci_total > 0 and ci_pass / ci_total < 0.75:
            return False
        return True

    @property
    def gate_score(self) -> float:
        if self.eliminated:
            return -1.0
        pr = self.pass_rate * 50
        ci_pass = self.critical_pass_count + self.important_pass_count
        cp = (ci_pass / max(self.total_configured_gates, 1)) * 20
        cc = (1 - self.cond_count / max(self.total_configured_gates, 1)) * 30
        return round(pr + cp + cc, 1)

    def to_json(self) -> Dict:
        return {
            "sequence": self.sequence,
            "eliminated": self.eliminated,
            "elimination_reason": self.elimination_reason,
            "overall_status": self.overall_status,
            "can_proceed": self.can_proceed,
            "pass_rate": round(self.pass_rate * 100, 1),
            "gate_score": self.gate_score,
            "critical_pass": self.critical_pass_count,
            "important_pass": self.important_pass_count,
            "cond_count": self.cond_count,
            "total_gates": self.total_configured_gates,
            "calibration_baselines": self.calibration_baselines,
            "gates": [
                {
                    "gate_id": gr.gate.gate_id,
                    "name": gr.gate.name,
                    "criticality": gr.gate.criticality.value,
                    "status": gr.status.value,
                    "score": gr.score,
                    "threshold_pass": gr.gate.pass_threshold,
                    "threshold_fail": gr.gate.fail_threshold,
                    "message": gr.message.split(" 💡")[0],
                    "suggestion": gr.suggestion,
                    "timestamp": gr.timestamp,
                }
                for gr in self.results
            ],
        }


# ── Gate Definitions ──

PENDP_GATES: List[GateDef] = [
    GateDef(
        gate_id="G1", name="靶向基序验证", dimension="D1",
        criticality=GateCriticality.CRITICAL,
        pass_threshold=6.0, fail_threshold=3.0,
        description="Target motif recognition (RGD/NGR/CendR/CD206/EGFR)",
        fail_message="无可识别靶向基序 — 递送系统无靶向能力",
        cond_suggestion="考虑引入 RGD/NGR/CendR 等已知靶向基序；或添加环化Cys提高特异性",
    ),
    GateDef(
        gate_id="G2", name="物化性质筛选", dimension="D2",
        criticality=GateCriticality.CRITICAL,
        pass_threshold=5.0, fail_threshold=3.0,
        description="MW ≤5000 Da, pI balance, solubility, disulfide stability",
        fail_message="物化性质极差 (MW>5000/溶解性/电荷失衡) — 不可成药",
        cond_suggestion="缩短序列至<30aa降低MW；增加带电残基改善溶解性；引入Cys二硫键稳定构象",
    ),
    GateDef(
        gate_id="G3", name="积雪草酸协同评估", dimension="D3",
        criticality=GateCriticality.NICE_TO_HAVE,
        pass_threshold=5.0, fail_threshold=2.0,
        description="Amphipathic helix, Arg/Lys content → AA-LNP synergy",
        fail_message="与积雪草酸-LNP协同性低",
        cond_suggestion="增加Arg/Lys残基(≥3个)增强内体逃逸；引入G/A/L构建双亲性螺旋",
    ),
    GateDef(
        gate_id="G4", name="蛋白冠+LNP兼容", dimension="D4",
        criticality=GateCriticality.CRITICAL,
        pass_threshold=5.0, fail_threshold=3.0,
        description="Protein corona compatibility, LNP surface display",
        fail_message="LNP兼容性极差 — 递送系统核心功能失效",
        cond_suggestion="增加Arg/Lys比例(>20%)促进蛋白冠；调整疏水比例至0.25-0.45；引入G/P增加柔性",
    ),
    GateDef(
        gate_id="G5", name="脱靶风险控制", dimension="D5",
        criticality=GateCriticality.IMPORTANT,
        pass_threshold=5.0, fail_threshold=3.0,
        description="Off-target binding risk (specificity, length, polycationic)",
        fail_message="脱靶风险过高 — 可能引起系统性毒性",
        cond_suggestion="延长序列至≥7aa提高特异性；减少Arg/Lys比例(≤30%)降低多阳离子风险",
    ),
    GateDef(
        gate_id="G6", name="合成可行性", dimension="D6",
        criticality=GateCriticality.IMPORTANT,
        pass_threshold=5.0, fail_threshold=3.0,
        description="Length, hydrophobic stretches, aggregation propensity",
        fail_message="合成难度过高 — 产率/纯度不可控",
        cond_suggestion="缩短至≤12aa；打断连续疏水段(>4个)；减少Y/V/I/F含量降低聚集",
    ),
    GateDef(
        gate_id="G7", name="ESM相似度参考", dimension="D7",
        criticality=GateCriticality.NICE_TO_HAVE,
        pass_threshold=5.0, fail_threshold=1.0,
        description="ESM-2 embedding similarity to reference peptides",
        fail_message="ESM相似度极低 — 序列空间远离已知功能肽",
        cond_suggestion="考虑引入已知功能肽的保守序列片段；从肺靶向数据库选择骨架进行修饰",
    ),
    GateDef(
        gate_id="G8", name="偶联方向定向性", dimension="D9",
        criticality=GateCriticality.NICE_TO_HAVE,
        pass_threshold=5.0, fail_threshold=2.0,
        description="Oriented conjugation (Cys placement, internal Lys count)",
        fail_message="偶联方向性差 — 可能降低LNP表面展示效率",
        cond_suggestion="在C端添加Cys用于maleimide定点偶联；减少内部Lys(≤1个)避免多点连接",
    ),
]


def _make_gates() -> List[GateDef]:
    """Create a fresh deep copy of gate definitions (V4 fix: no shared mutation)."""
    return deepcopy(PENDP_GATES)


class GatePipeline:
    """Execute gate pipeline with calibration, logging, and smart suggestions."""

    def __init__(self, gates: List[GateDef] = None, log_json: bool = False):
        self.gates = gates if gates is not None else _make_gates()
        self.log_json = log_json
        self.json_records: List[Dict] = []
        self._calibration: Dict[str, Dict] = {}
        self.total_configured = len(self.gates)

    # ── V4: G0 Calibration (returns a NEW calibrated pipeline) ──

    def calibrate(self, scoring_engine=None) -> "GatePipeline":
        """G0: Run reference peptides and return a NEW calibrated pipeline.

        Original pipeline is NOT mutated. The returned pipeline has
        thresholds adjusted based on reference peptide baselines.
        """
        if scoring_engine is None:
            from pendp.scoring.engine import ScoringEngine
            scoring_engine = ScoringEngine()

        calib = {}
        print("\n🔬 G0 Calibration — Reference Peptides")
        print("═" * 60)

        for name, seq in REFERENCE_PEPTIDES.items():
            result = scoring_engine.score_sequence(seq)
            calib[name] = {
                "sequence": seq,
                "total": result["total_score"],
                "dimensions": {
                    dim_id: d["score"]
                    for dim_id, d in result["dimensions"].items()
                },
            }
            print(f"  {name:10s} ({seq:12s})  total={result['total_score']:5.1f}")

        dim_stats = {}
        all_dim_ids = sorted(calib[list(calib.keys())[0]]["dimensions"].keys())
        for dim_id in all_dim_ids:
            scores = [calib[name]["dimensions"].get(dim_id, 0) for name in calib]
            dim_stats[dim_id] = {
                "mean": round(statistics.mean(scores), 1),
                "stdev": round(statistics.stdev(scores), 1) if len(scores) > 1 else 0.0,
                "min": round(min(scores), 1),
                "max": round(max(scores), 1),
                "p25": round(_percentile(scores, 25), 1),
                "p75": round(_percentile(scores, 75), 1),
            }

        # Create new calibrated gates (deep copy, no mutation of originals)
        new_gates = deepcopy(self.gates)
        adjustments = []
        for gate_def in new_gates:
            dim_id = gate_def.dimension
            if dim_id in dim_stats:
                ref_p25 = dim_stats[dim_id]["p25"]
                if ref_p25 < gate_def.pass_threshold:
                    old = gate_def.pass_threshold
                    gate_def.pass_threshold = max(ref_p25, gate_def.fail_threshold + 0.5)
                    adjustments.append(
                        f"  {gate_def.gate_id} pass: {old:.1f}→{gate_def.pass_threshold:.1f} "
                        f"(ref p25={ref_p25:.1f})"
                    )

        if adjustments:
            print(f"\n📐 Threshold adjustments ({len(adjustments)}):")
            for adj in adjustments:
                print(adj)

        print(f"\n📊 Per-dimension baselines:")
        print(f"  {'Dim':4s} {'Mean':>5s} {'Stdev':>5s} {'Min':>5s} {'Max':>5s} {'P25':>5s} {'P75':>5s}")
        for dim_id in all_dim_ids:
            s = dim_stats[dim_id]
            print(f"  {dim_id:4s} {s['mean']:5.1f} {s['stdev']:5.1f} {s['min']:5.1f} {s['max']:5.1f} {s['p25']:5.1f} {s['p75']:5.1f}")

        # Return new calibrated pipeline
        calibrated = GatePipeline(gates=new_gates, log_json=self.log_json)
        calibrated._calibration = dim_stats
        # Log calibration to JSON if requested
        if self.log_json:
            calibrated.json_records.append({
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "event": "G0_calibration",
                "reference_count": len(REFERENCE_PEPTIDES),
                "adjustments": [a.strip() for a in adjustments],
                "baselines": {k: {"mean": v["mean"], "p25": v["p25"]} for k, v in dim_stats.items()},
            })
        return calibrated

    # ── Core evaluation ──

    def evaluate(self, dimension_scores: Dict[str, float],
                 sequence: str = "") -> GatePipelineResult:
        """Run all gates against dimension scores.

        After critical FAIL, remaining gates are appended as SKIP for
        audit consistency.
        """
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        result = GatePipelineResult(sequence=sequence, total_configured_gates=self.total_configured)
        if self._calibration:
            result.calibration_baselines = self._calibration

        eliminated_idx = -1
        for i, gate_def in enumerate(self.gates):
            if eliminated_idx >= 0:
                # Append SKIP for remaining gates
                gate_result = GateResult(
                    gate=gate_def, status=GateStatus.SKIP, score=0.0,
                    message=f"┄ {gate_def.name}: SKIPPED (eliminated at G{eliminated_idx+1})",
                    timestamp=ts,
                )
                result.results.append(gate_result)
                continue

            score = dimension_scores.get(gate_def.dimension, 0.0)
            status, message = gate_def.decide(score)
            gate_result = GateResult(
                gate=gate_def, status=status, score=score, message=message,
                suggestion=gate_def.cond_suggestion if status == GateStatus.COND else "",
                timestamp=ts,
            )
            result.results.append(gate_result)

            if self.log_json:
                self.json_records.append({
                    "ts": ts, "seq": sequence,
                    "gate": gate_def.gate_id, "dim": gate_def.dimension,
                    "status": status.value, "score": score,
                    "pass_threshold": gate_def.pass_threshold,
                    "fail_threshold": gate_def.fail_threshold,
                })

            if status == GateStatus.PASS:
                if gate_def.criticality == GateCriticality.CRITICAL:
                    result.critical_pass_count += 1
                elif gate_def.criticality == GateCriticality.IMPORTANT:
                    result.important_pass_count += 1
            elif status == GateStatus.COND:
                result.cond_count += 1
            elif status == GateStatus.FAIL:
                if gate_def.criticality == GateCriticality.CRITICAL:
                    result.critical_fail_count += 1
                    result.eliminated = True
                    result.elimination_reason = (
                        f"GATE {gate_def.gate_id} ({gate_def.name}) CRITICAL FAIL: "
                        f"score={score:.1f} < {gate_def.fail_threshold} — "
                        f"{gate_def.fail_message}"
                    )
                    eliminated_idx = i  # Mark for SKIP on subsequent gates

        return result

    # ── V4: Batch evaluation ──

    def evaluate_batch(self, sequences: Dict[str, str],
                       scoring_engine=None) -> List[Tuple[str, GatePipelineResult, float]]:
        if scoring_engine is None:
            from pendp.scoring.engine import ScoringEngine
            scoring_engine = ScoringEngine()

        ranked = []
        for name, seq in sequences.items():
            sr = scoring_engine.score_sequence(seq)
            dim_scores = {dim_id: d["score"] for dim_id, d in sr["dimensions"].items()}
            gate_result = self.evaluate(dim_scores, seq)
            combined = gate_result.gate_score + sr["total_score"]
            ranked.append((name, gate_result, combined))

        ranked.sort(key=lambda x: (x[1].eliminated, -x[2]))
        return ranked

    # ── Display ──

    def summary(self, result: GatePipelineResult) -> str:
        lines = [
            f"\n{'═'*60}",
            f"🔬 PENdp V4 Gate Pipeline — {result.sequence or 'unknown'}",
            f"{'═'*60}",
        ]
        for gr in result.results:
            icon = {"PASS": "✅", "FAIL": "❌", "COND": "⚠️", "SKIP": "┄"}[gr.status.value]
            criticality_tag = {
                GateCriticality.CRITICAL: "[!!]",
                GateCriticality.IMPORTANT: "[! ]",
                GateCriticality.NICE_TO_HAVE: "[  ]",
            }[gr.gate.criticality]
            lines.append(f"  {icon} {gr.gate.gate_id} {criticality_tag} {gr.gate.name:14s}  "
                         f"{gr.score:4.1f}/10  {gr.message.split(' 💡')[0]}")
            if gr.status == GateStatus.COND and gr.suggestion:
                lines.append(f"       💡 {gr.suggestion}")

        ci_pass = result.critical_pass_count + result.important_pass_count
        lines.append(f"{'─'*60}")
        lines.append(f"  {result.overall_status}  (gate_score={result.gate_score:.1f})")
        if result.eliminated:
            lines.append(f"  ⛔ {result.elimination_reason}")
        elif not result.can_proceed:
            lines.append(f"  ⛔ 关键+重要门通过率 <75% — 不建议推进湿实验")
        else:
            lines.append(f"  ✅ 可以推进下一步 (CI-PASS={ci_pass}/{self.total_configured})")
        lines.append(f"{'═'*60}")
        return "\n".join(lines)

    def batch_summary(self, ranked: List[Tuple[str, GatePipelineResult, float]],
                      top_n: int = 10) -> str:
        lines = [
            f"\n{'═'*70}",
            f"🔬 PENdp V4 Batch Gate Ranking — Top {min(top_n, len(ranked))}",
            f"{'═'*70}",
            f"  {'Rank':4s} {'Name':20s} {'Gate':10s} {'Total':>6s} {'Score':>6s}  Status",
            f"  {'─'*4} {'─'*20} {'─'*10} {'─'*6} {'─'*6}  {'─'*20}",
        ]
        for i, (name, gr, combined) in enumerate(ranked[:top_n], 1):
            lines.append(
                f"  {i:4d} {name:20s} {gr.gate_score:6.1f}/100 {combined - gr.gate_score:6.1f} "
                f"{combined:6.1f}  {gr.overall_status}"
            )
        lines.append(f"{'═'*70}")
        return "\n".join(lines)

    def flush_json(self) -> str:
        return "\n".join(json.dumps(r, ensure_ascii=False) for r in self.json_records)


# ── Helpers ──

def _percentile(data: List[float], p: float) -> float:
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * p / 100.0
    f = int(k)
    c = k - f
    if f + 1 < len(sorted_data):
        return sorted_data[f] + c * (sorted_data[f + 1] - sorted_data[f])
    return sorted_data[f]


def evaluate_gates(seq: str, dimension_scores: Dict[str, float],
                   log_json: bool = False) -> GatePipelineResult:
    pipeline = GatePipeline(log_json=log_json)
    return pipeline.evaluate(dimension_scores, seq)
