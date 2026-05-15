"""
PENdp 决策框架 — 五大靶向子系统 + 管线优先级 + 对赌决策

来源: pendp-peptide-design Skill §一B（认知升级融合）
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional


# ── 五大靶向子系统 ──

@dataclass
class TargetingSubSystem:
    """A targeting subsystem (organ/disease area)."""
    name: str
    organ: str
    core_targets: List[str]
    top_indication: str
    secondary_indications: List[str] = field(default_factory=list)
    key_ligands: List[str] = field(default_factory=list)
    pendp_advantage: str = ""
    rationale: str = ""


SUBSYSTEMS: List[TargetingSubSystem] = [
    TargetingSubSystem(
        name="肺靶向", organ="🫁 肺",
        core_targets=["NRP-1", "αvβ3/β5", "EGFR", "CD206"],
        top_indication="IPF (肺纤维化) 🥇",
        secondary_indications=["NSCLC 🥈", "肺转移"],
        key_ligands=["iRGD", "iNGR", "RP-832c", "GE11"],
        pendp_advantage="数据最完整，积雪草酸+ELP+多肽均有实验方案",
        rationale="Johns Hopkins验证mRNA+CD206靶向IPF，无同类核酸竞争"),
    TargetingSubSystem(
        name="脑靶向", organ="🧠 脑",
        core_targets=["LRP1", "TfR1"],
        top_indication="GBM (胶质母细胞瘤) 🥇",
        secondary_indications=["阿尔茨海默"],
        key_ligands=["Angiopep-2"],
        pendp_advantage="ANG1005概念已验证BBB穿透",
        rationale="BBB是最大挑战，但Angiopep-2有临床验证数据"),
    TargetingSubSystem(
        name="肝靶向", organ="🫁 肝",
        core_targets=["ASGPR", "αvβ6", "GPC3"],
        top_indication="IMLD/MMA 🥇",
        secondary_indications=["HCC", "代谢性疾病"],
        key_ligands=["GalNAc"],
        pendp_advantage="标准PENdp即可（'去肝化'优先）",
        rationale="标准LNP 70-90%优先肝趋向，IMLD/MMA是利用而非对抗LNP天然趋势"),
    TargetingSubSystem(
        name="脾/免疫", organ="🫘 脾",
        core_targets=["CD169", "DEC-205"],
        top_indication="mRNA肿瘤疫苗 🥇",
        secondary_indications=["传染病疫苗", "自身免疫"],
        key_ligands=[],
        pendp_advantage="免疫治疗激活，脾靶向DC细胞",
        rationale="赛道已拥挤(Moderna/BioNTech Phase III)，需差异化"),
    TargetingSubSystem(
        name="心/肾", organ="❤️ 心/肾",
        core_targets=["Megalin", "NEP"],
        top_indication="ADPKD (多囊肾病) 🥇",
        secondary_indications=["心衰", "肾纤维化"],
        key_ligands=[],
        pendp_advantage="积雪草酸增强溶酶体逃逸",
        rationale="2025年NHP数据火热，临床需求强"),
]


# ── 管线优先级推荐 ──

@dataclass
class PipelineRecommendation:
    rank: int
    indication: str
    targeting_strategy: str
    key_ligand: str
    rationale: str
    timeline: str = ""
    estimated_cost: str = ""


PIPELINE_RECOMMENDATIONS: List[PipelineRecommendation] = [
    PipelineRecommendation(
        rank=1, indication="IPF (肺纤维化)",
        targeting_strategy="CD206/RP-832c",
        key_ligand="RP-832c",
        rationale="无同类核酸竞争，临床需求强，Johns Hopkins验证mRNA+CD206靶向",
        timeline="Week 1-16",
        estimated_cost="中等 (合成+细胞+小鼠)"),
    PipelineRecommendation(
        rank=2, indication="IMLD/MMA (代谢病)",
        targeting_strategy="标准PENdp (利用LNP肝趋向)",
        key_ligand="—",
        rationale="最快验证平台基础功能，3-5K成本，8周出数据",
        timeline="Week 1-8",
        estimated_cost="低 (3-5K)"),
    PipelineRecommendation(
        rank=3, indication="NSCLC (非小细胞肺癌)",
        targeting_strategy="EGFR/GE11 + iRGD",
        key_ligand="GE11",
        rationale="最大患者群(40-80% EGFR+)，但竞争激烈，需差异化",
        timeline="Month 3-9",
        estimated_cost="高"),
    PipelineRecommendation(
        rank=4, indication="ADPKD (多囊肾病)",
        targeting_strategy="Megalin",
        key_ligand="—",
        rationale="2025年NHP数据火热，积雪草酸增强溶酶体逃逸",
        timeline="Month 6-12",
        estimated_cost="高"),
    PipelineRecommendation(
        rank=5, indication="HCC (肝癌)",
        targeting_strategy="ASGPR/GPC3",
        key_ligand="GalNAc",
        rationale="有上市药物验证，但差异化需靠多靶点组合",
        timeline="Month 6+",
        estimated_cost="高"),
]


# ── 对赌式决策框架 ──

class DecisionFramework:
    """Disease-first decision framework.

    核心哲学：先用疾病视角选方向，再用多肽视角选具体序列。
    两个框架互补不矛盾。
    """

    @staticmethod
    def evaluate_indication(indication: str) -> Dict:
        """Evaluate an indication using 5-dimension decision framework.

        Dimensions:
        1. 临床确定性 — 是否有前人验证过类似路径？
        2. 执行难度 — 需要多少步创新？需要什么资源？
        3. 差异化价值 — 同类竞品多吗？护城河够不够深？
        4. 市场窗口 — 现在不做会被人占吗？还是可以等？
        5. 决策灵活性 — 万一失败，损失多大？能否转向？
        """
        # Find recommendation
        recs = {r.indication: r for r in PIPELINE_RECOMMENDATIONS}
        rec = recs.get(indication)

        scores = {
            "临床确定性": 0,
            "执行难度": 0,
            "差异化价值": 0,
            "市场窗口": 0,
            "决策灵活性": 0,
        }

        # Score based on indication characteristics
        if "IPF" in indication:
            scores = {"临床确定性": 7, "执行难度": 6,
                      "差异化价值": 9, "市场窗口": 8,
                      "决策灵活性": 7}
        elif "IMLD" in indication or "MMA" in indication:
            scores = {"临床确定性": 8, "执行难度": 9,
                      "差异化价值": 6, "市场窗口": 7,
                      "决策灵活性": 9}
        elif "NSCLC" in indication:
            scores = {"临床确定性": 6, "执行难度": 5,
                      "差异化价值": 4, "市场窗口": 5,
                      "决策灵活性": 5}
        elif "ADPKD" in indication:
            scores = {"临床确定性": 5, "执行难度": 4,
                      "差异化价值": 8, "市场窗口": 9,
                      "决策灵活性": 6}

        total = sum(scores.values()) / 5

        return {
            "indication": indication,
            "dimensions": scores,
            "average_score": round(total, 1),
            "recommendation": rec,
            "decision": "推进" if total >= 6 else ("观察" if total >= 4 else "暂缓"),
        }

    def compare_indications(self, *indications: str) -> List[Dict]:
        """Compare multiple indications side-by-side."""
        results = [self.evaluate_indication(ind) for ind in indications]
        results.sort(key=lambda x: x["average_score"], reverse=True)
        return results

    def suggest_parallel_paths(self) -> List[Dict]:
        """Suggest parallel pipeline paths.

        Recommended strategy: run 2 low-cost paths in parallel,
        gather data at week 8, then decide next step.
        """
        return [
            {
                "path": "快速验证 (IPF直奔主题)",
                "indications": ["IPF (肺纤维化)"],
                "cost": "中等",
                "timeline": "Week 1-16",
                "rationale": "IPF无同类核酸竞争，数据最强",
                "parallel_with": "平台验证",
            },
            {
                "path": "平台验证 (IMLD低成本)",
                "indications": ["IMLD/MMA (代谢病)"],
                "cost": "低 (3-5K)",
                "timeline": "Week 1-8",
                "rationale": "利用LNP天然肝趋向，最快验证PENdp基础功能",
                "parallel_with": "快速验证",
            },
            {
                "path": "差异化 (NSCLC高回报)",
                "indications": ["NSCLC (非小细胞肺癌)"],
                "cost": "高",
                "timeline": "Month 3-9",
                "rationale": "最大患者群，但竞争激烈",
                "parallel_with": "—",
            },
        ]


# ── 肝靶向特殊警示 ──

LIVER_TARGETING_CAVEAT = """
⚠️ 肝靶向特殊警示：
标准LNP 70-90%优先肝趋向，所以肝靶向对PENdp是"去肝化"而非"加靶向"。
IMLD/MMA是利用而非对抗LNP天然趋势。这与其他器官的靶向策略完全不同——其他器官需要主动靶向，肝只需要"不去肝"。
"""


# ── 快速查询接口 ──

def get_subsystem(organ_name: str) -> Optional[TargetingSubSystem]:
    """Find a targeting subsystem by organ name."""
    for s in SUBSYSTEMS:
        if organ_name in s.name or organ_name in s.organ:
            return s
    return None


def list_subsystems() -> List[Dict]:
    """Return all subsystems as dicts for display."""
    return [
        {
            "name": s.name,
            "organ": s.organ,
            "top_indication": s.top_indication,
            "core_targets": s.core_targets,
            "key_ligands": s.key_ligands,
            "advantage": s.pendp_advantage,
        }
        for s in SUBSYSTEMS
    ]


def pipeline_summary() -> List[Dict]:
    """Return pipeline priorities for display."""
    return [
        {
            "rank": r.rank,
            "indication": r.indication,
            "strategy": r.targeting_strategy,
            "ligand": r.key_ligand,
            "rationale": r.rationale,
            "timeline": r.timeline,
        }
        for r in PIPELINE_RECOMMENDATIONS
    ]
