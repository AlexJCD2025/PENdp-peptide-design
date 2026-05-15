"""
PENdp Target Knowledge Graph — 受体-疾病-配体矩阵

完整的靶点知识图谱，支持靶点查询、疾病匹配、配体推荐。
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class Target:
    """A biological target/receptor."""
    name: str
    aliases: List[str] = field(default_factory=list)
    organ: str = ""
    diseases: List[str] = field(default_factory=list)
    ligands: List[str] = field(default_factory=list)
    priority: int = 3  # 1-5 stars
    notes: str = ""


# ── Target knowledge graph ──
TARGETS: List[Target] = [
    Target("NRP-1", ["Neuropilin-1"], "肺/肿瘤/脑",
           ["NSCLC", "GBM", "乳腺癌", "肺纤维化"],
           ["iRGD", "tLyP-1", "RPARPAR", "iNGR"], 5,
           "CendR通路核心受体, 跨内皮转运+肿瘤深部穿透"),
    Target("αvβ3/β5", ["Integrin αvβ3", "Integrin αvβ5"], "肿瘤血管/肺",
           ["实体瘤", "转移", "肺纤维化"],
           ["iRGD", "iNGR", "CREKA"], 5,
           "肿瘤血管高表达, RGD基序经典靶点"),
    Target("CD13", ["Aminopeptidase N", "ANPEP"], "肿瘤血管/肾",
           ["肝癌", "肾癌", "血管新生"],
           ["NGR", "iNGR"], 4,
           "NGR基序靶点, 肿瘤血管特异性"),
    Target("EGFR", ["ErbB1", "HER1"], "肺/乳腺/结直肠",
           ["NSCLC(40-80% EGFR+)", "乳腺癌", "结直肠癌"],
           ["GE11", "DPG3"], 4,
           "NSCLC最大患者群, GE11已验证LNP修饰"),
    Target("CD206", ["MRC1", "MRC1"], "肺/肝/脾",
           ["肺纤维化(IPF)", "M2巨噬细胞相关疾病"],
           ["RP-832c"], 4,
           "IPF第一管线靶点, M2巨噬细胞标志物"),
    Target("p32", ["gC1qR", "C1qBP"], "肿瘤/M2巨噬",
           ["多种实体瘤", "胶质瘤"],
           ["AKPC", "LinTT1", "CKRGARSTC"], 4,
           "LNP表面修饰验证靶点(ACS Nano 2024)"),
    Target("LRP1", ["LRP1"], "脑/肝",
           ["GBM", "阿尔茨海默"],
           ["Angiopep-2"], 4,
           "BBB穿透经典靶点, ANG1005概念验证"),
    Target("ASGPR", ["ASGR1"], "肝",
           ["HCC", "IMLD", "MMA"],
           ["GalNAc", "Lactose"], 3,
           "肝靶向金标准, 标准LNP天然肝趋向"),
    Target("CD44", ["CD44"], "肿瘤/免疫",
           ["肿瘤干细胞", "乳腺癌"],
           ["A6(KPSSPPEE)"], 3,
           "透明质酸受体, 肿瘤干细胞靶点"),
    Target("CD169", ["Siglec-1"], "脾/免疫",
           ["病毒感染", "肿瘤免疫"],
           [], 3,
           "脾靶向免疫激活, mRNA肿瘤疫苗潜在靶点"),
    Target("DEC-205", ["CD205", "LY75"], "脾/免疫",
           ["肿瘤免疫", "自身免疫"],
           [], 3,
           "树突状细胞靶向, 抗原递呈增强"),
    Target("Megalin", ["LRP2"], "肾",
           ["ADPKD", "肾纤维化"],
           [], 3,
           "肾脏靶向, ADPKD治疗潜在靶点"),
    Target("NEP", ["Neprilysin", "MME"], "心/肾",
           ["心衰", "高血压"],
           [], 2,
           "心脏保护, 心衰治疗靶点"),
    Target("TfR1", ["Transferrin Receptor"], "脑",
           ["GBM", "阿尔茨海默"],
           [], 3,
           "BBB转铁蛋白受体, 脑靶向替代路径"),
    Target("Folate Receptor", ["FRα", "FOLR1"], "肿瘤",
           ["卵巢癌", "NSCLC"],
           ["Folate"], 2,
           "叶酸受体, 经典肿瘤靶点, PENdp非优先"),
]


class TargetKnowledgeGraph:
    """Knowledge graph for targets, diseases, and peptides."""

    def __init__(self, targets: List[Target] = None):
        self._targets = targets or TARGETS
        self._by_name = {t.name: t for t in self._targets}
        for t in self._targets:
            for alias in t.aliases:
                self._by_name[alias] = t

    # ── Queries ──

    def by_disease(self, disease: str) -> List[Target]:
        """Find all targets associated with a disease."""
        d = disease.lower()
        return [t for t in self._targets
                if any(d in dis.lower() for dis in t.diseases)]

    def by_organ(self, organ: str) -> List[Target]:
        """Find all targets in an organ."""
        return [t for t in self._targets if organ in t.organ]

    def get_target(self, name: str) -> Optional[Target]:
        return self._by_name.get(name)

    def ligands_for_disease(self, disease: str) -> List[str]:
        """Get all peptide ligands for a disease's targets."""
        targets = self.by_disease(disease)
        ligands = set()
        for t in targets:
            ligands.update(t.ligands)
        return sorted(ligands)

    def top_targets(self, n: int = 5) -> List[Target]:
        """Top targets by priority score."""
        return sorted(self._targets, key=lambda t: t.priority, reverse=True)[:n]

    def summary(self) -> Dict:
        """Summary statistics."""
        return {
            "total_targets": len(self._targets),
            "organs_covered": list(set(t.organ for t in self._targets)),
            "peptide_ligands": list(set(l for t in self._targets for l in t.ligands)),
            "diseases": list(set(d for t in self._targets for d in t.diseases)),
        }

    def disease_matrix(self) -> Dict[str, List[Dict]]:
        """Return disease → [{target, ligands, priority}] matrix."""
        disease_map = {}
        for t in self._targets:
            for disease in t.diseases:
                if disease not in disease_map:
                    disease_map[disease] = []
                disease_map[disease].append({
                    "target": t.name,
                    "ligands": t.ligands,
                    "priority": t.priority,
                })
        return disease_map

    # ── PENdp priority recommendation ──
    def prioritize_for_pendp(self) -> List[Dict]:
        """
        PENdp-specific target prioritization:
        1. Lung + tumor targets first
        2. Has verified peptide ligands
        3. High priority score
        """
        scored = []
        for t in self._targets:
            lung_score = 2 if "肺" in t.organ else 0
            ligand_score = min(len(t.ligands), 3)  # max 3
            has_verified = 2 if any(l in ["iRGD","iNGR","AKPC","GE11","RP-832c"]
                                    for l in t.ligands) else 0
            total = t.priority + lung_score + ligand_score + has_verified
            scored.append({
                "target": t.name,
                "organ": t.organ,
                "priority_raw": t.priority,
                "score": total,
                "top_ligand": t.ligands[0] if t.ligands else "",
                "diseases": t.diseases[:3],
            })
        return sorted(scored, key=lambda x: x["score"], reverse=True)
