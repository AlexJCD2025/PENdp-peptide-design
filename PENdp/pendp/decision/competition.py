"""
PENdp 竞争对标 — 技术路线对比 + 竞争格局

来源: pendp-peptide-design Skill §五
"""
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Competitor:
    name: str
    category: str        # "platform" / "therapy" / "tool"
    targeting_strategy: str
    technology: str
    stage: str
    relationship: str    # 🔴最接近 / 🟡不同路径 / 🟢可合作 / 🔵集团内
    notes: str = ""


COMPETITORS: List[Competitor] = [
    Competitor("BreezeBio NanoGalaxy", "platform",
               "聚酰胺骨架+HNP", "多器官靶向+低免疫",
               "早期", "🔴 最接近竞品",
               "多器官靶向思路与PENdp重叠，但技术路线不同"),
    Competitor("ReCode SORT LNP", "platform",
               "脂质组成调控", "第5种脂质决定器官靶向",
               "临床前", "🟡 不同路径可互补",
               "通过改变脂质比例实现器官靶向，与PENdp的多肽修饰互补"),
    Competitor("MOLEA (论文)", "tool",
               "AI优化LNP配方", "多目标Pareto优化",
               "开源论文", "🟢 可合作",
               "GitHub开源，可集成到PENdp的QSAR阶段"),
    Competitor("ASSET Protocol (论文)", "platform",
               "抗体定向LNP", "工程化scFv固定到LNP表面",
               "论文阶段", "🟡 概念参考",
               "偶联方向策略可借鉴(D9评分维度来源)"),
    Competitor("欣肽生物 SAPdp", "platform",
               "多肽递送", "自组装多肽骨架",
               "早期研发", "🔵 集团内协同",
               "欣肽内部另一条管线，与PENdp技术互补"),
    Competitor("Moderna mRNA疫苗", "therapy",
               "个性化mRNA+脂质纳米颗粒", "已进入Phase III",
               "Phase III", "🔴 赛道拥挤",
               "肿瘤疫苗赛道拥挤验证了mRNA递送趋势"),
    Competitor("BioNTech mRNA疫苗", "therapy",
               "个性化mRNA+脂质纳米颗粒", "计划拆分上市",
               "Phase III", "🔴 赛道拥挤",
               "胰腺癌疫苗6年持久响应"),
]


class CompetitiveLandscape:
    """Competitive analysis for PENdp."""

    @staticmethod
    def by_category(category: str) -> List[Competitor]:
        return [c for c in COMPETITORS if c.category == category]

    @staticmethod
    def closest_competitors() -> List[Competitor]:
        return [c for c in COMPETITORS if "🔴" in c.relationship]

    @staticmethod
    def summary() -> Dict:
        return {
            "total": len(COMPETITORS),
            "platforms": len([c for c in COMPETITORS if c.category == "platform"]),
            "therapies": len([c for c in COMPETITORS if c.category == "therapy"]),
            "closest": [c.name for c in COMPETITORS if "🔴" in c.relationship],
            "collaboration": [c.name for c in COMPETITORS if "🟢" in c.relationship],
        }

    @staticmethod
    def ipf_landscape() -> Dict:
        """IPF-specific competition analysis."""
        return {
            "nucleic_acid_competitors": "无已知同类核酸竞争",
            "small_molecule": "吡非尼酮、尼达尼布已上市(仅有减缓疾病进展)",
            "biologic": "多种单抗在临床(IL-13, CTGF等)",
            "implication": "mRNA+CD206靶向在IPF领域是差异化路径",
            "validation": "Johns Hopkins已发表mRNA+CD206概念验证数据",
        }
