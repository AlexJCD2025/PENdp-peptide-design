"""
PENdp 文献追踪 — 关键论文数据库

来源: pendp-peptide-design Skill §三
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Paper:
    title: str
    authors: str
    source: str
    year: int
    doi: str = ""
    relevance_to_pendp: str = ""
    key_finding: str = ""
    priority: str = "medium"


PAPERS: List[Paper] = [
    Paper(
        title="The landscape for therapeutic cancer vaccines",
        authors="Congzhou Chen 等 (清华大学+CDE)",
        source="Nat. Rev. Drug Discov. (From the Analyst's Couch)",
        year=2026,
        doi="10.1038/d41573-026-00063-z",
        relevance_to_pendp="mRNA递送技术突破验证了LNP平台的趋势; 肿瘤疫苗赛道已拥挤",
        key_finding="Moderna个性化mRNA疫苗Phase III, 黑色素瘤5年降低49%风险; BioNTech计划拆分上市; MSKCC胰腺癌疫苗6年持久响应",
        priority="high",
    ),
    Paper(
        title="CendR peptide-mediated tumor penetration",
        authors="Ruoslahti E",
        source="Nature Reviews Cancer",
        year=2010,
        relevance_to_pendp="iRGD/iNGR的CendR穿透机制核心文献",
        key_finding="RGD→αvβ3 → 切割暴露CendR → NRP-1结合 → 跨内皮转运",
        priority="high",
    ),
    Paper(
        title="AKPC-modified LNP for CD44-targeted RNA delivery",
        authors="Zhao et al.",
        source="ACS Nano 2025, 19(14), 13685-13704",
        year=2025,
        doi="10.1021/acsnano.4c14625",
        relevance_to_pendp="AKPC/KPSSPPEE作为LNP表面修饰多肽的验证数据; 实际靶点CD44(非p32)",
        key_finding="KPSSPPEE (A6肽)修饰LNP靶向CD44,增强RNA药物抗肿瘤效力",
        priority="high",
    ),
    Paper(
        title="RP-832c targeting CD206 for IPF therapy",
        authors="—",
        source="Johns Hopkins / 多篇",
        year=2025,
        relevance_to_pendp="IPF第一管线的靶向策略依据",
        key_finding="CD206靶向多肽RP-832c在IPF模型中减少纤维化",
        priority="high",
    ),
    Paper(
        title="MOLEA: Multi-Objective Optimization for LNP Engineering",
        authors="Muye Zhou, Yue Xu, Gen Li, Bowen Li Lab",
        source="Nature Biotechnology, 2026",
        year=2026,
        doi="10.1038/s41587-026-03109-0",
        relevance_to_pendp="AI优化LNP配方，可集成到PENdp的QSAR阶段; 器官选择性mRNA递送",
        key_finding="多目标Pareto优化同时优化效力、靶向性和安全性; 实现组织选择性mRNA递送",
        priority="medium",
    ),
    Paper(
        title="ASSET Protocol: Antibody-directed LNP Delivery",
        authors="Veiga N, Goldsmith M, Granot Y, et al.",
        source="Nature Communications, 2018, 9:4493",
        year=2018,
        doi="10.1038/s41467-018-06936-1",
        relevance_to_pendp="偶联方向策略——D9评分维度来源; scFv固定到LNP表面实现免疫细胞靶向",
        key_finding="工程化scFv固定到LNP表面通过CD3/CD4实现T细胞特异性靶向",
        priority="medium",
    ),
    Paper(
        title="2025年度药品审评报告 (NMPA/CDE)",
        authors="国家药监局药品审评中心",
        source="CDE官方网站",
        year=2026,
        relevance_to_pendp="核酸LNP递送审评通道未饱和;多肽药列为四大创新方向之一;附条件批准路径成熟",
        key_finding="2025年无LNP核酸药物获批;多肽药有专项指导原则;创新药76个获批",
        priority="high",
    ),
]


class LiteratureDatabase:
    """Key papers relevant to PENdp development."""

    @staticmethod
    def by_priority(priority: str = "high") -> List[Paper]:
        return [p for p in PAPERS if p.priority == priority]

    @staticmethod
    def search(query: str) -> List[Paper]:
        q = query.lower()
        return [p for p in PAPERS
                if q in p.title.lower() or q in p.authors.lower()
                or q in p.relevance_to_pendp.lower()]

    @staticmethod
    def summary() -> dict:
        return {
            "total": len(PAPERS),
            "high": len([p for p in PAPERS if p.priority == "high"]),
            "medium": len([p for p in PAPERS if p.priority == "medium"]),
            "low": len([p for p in PAPERS if p.priority == "low"]),
        }

    @staticmethod
    def export_markdown() -> str:
        lines = ["# PENdp 文献追踪\n", ""]
        for i, p in enumerate(PAPERS, 1):
            lines.append(f"### {i}. {p.title}")
            lines.append(f"**作者:** {p.authors}")
            lines.append(f"**来源:** {p.source} ({p.year})")
            if p.doi:
                lines.append(f"**DOI:** [{p.doi}](https://doi.org/{p.doi})")
            lines.append(f"**PENdp关联:** {p.relevance_to_pendp}")
            lines.append(f"**核心发现:** {p.key_finding}")
            lines.append("")
        return "\n".join(lines)
