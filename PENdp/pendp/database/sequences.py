"""
PENdp Lung-Targeting Peptide Database v6

18 core sequences with full annotations, 7-dimension scores, and target data.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

@dataclass
class PeptideEntry:
    """A single peptide entry in the database."""
    rank: int
    name: str
    sequence: str
    structure_type: str  # "环肽" or "线性"
    target: str
    target_detail: str
    molecular_weight: float
    score_total: float
    scores: List[float]  # 7-dimension scores [D1..D7]
    mechanism: str = ""
    references: List[str] = field(default_factory=list)
    priority: str = "medium"  # high/medium/low

    @property
    def meets_synthesis_threshold(self) -> bool:
        return self.score_total >= 65.0


# ── Lung-targeting database v6 ──
LUNG_PEPTIDES_V6: List[PeptideEntry] = [
    PeptideEntry(
        rank=1, name="iRGD", sequence="CRGDKGPDC",
        structure_type="环肽", target="αvβ3/αvβ5+NRP-1",
        target_detail="αvβ3/β5整合素 + NRP-1 (CendR双重靶向)",
        molecular_weight=1093.2, score_total=88.6,
        scores=[9.5, 9.0, 9.0, 8.5, 8.0, 8.5, 10.0],
        mechanism="CendR: RGD→αvβ3 → 切割暴露CendR → NRP-1结合 → 跨内皮转运",
        priority="high"
    ),
    PeptideEntry(
        rank=2, name="iRGD-L", sequence="CRGDK",
        structure_type="线性", target="αvβ3/αvβ5+NRP-1",
        target_detail="iRGD线性片段",
        molecular_weight=650.0, score_total=72.1,
        scores=[7.0, 8.5, 7.0, 7.0, 7.0, 9.0, 8.5],
        priority="high"
    ),
    PeptideEntry(
        rank=3, name="iNGR", sequence="CRNGRGPDC",
        structure_type="环肽", target="CD13+NRP-1",
        target_detail="CD13(肿瘤血管) + NRP-1(CendR穿透) 双靶向",
        molecular_weight=1120.2, score_total=87.6,
        scores=[9.0, 8.8, 9.0, 8.0, 8.0, 8.5, 9.8],
        mechanism="NGR→CD13 + CendR→NRP-1, 双靶向协同穿透",
        priority="high"
    ),
    PeptideEntry(
        rank=4, name="NGR", sequence="CNGRC",
        structure_type="环肽", target="CD13/氨肽酶N",
        target_detail="CD13/aminopeptidase N",
        molecular_weight=680.0, score_total=68.4,
        scores=[7.5, 7.5, 6.0, 6.5, 7.0, 9.0, 7.5],
        priority="medium"
    ),
    PeptideEntry(
        rank=5, name="CREKA", sequence="CREKA",
        structure_type="环肽", target="纤维蛋白",
        target_detail="肿瘤微环境中纤维蛋白-纤连蛋白",
        molecular_weight=680.0, score_total=66.5,
        scores=[7.0, 7.5, 7.0, 6.5, 6.5, 8.5, 7.0],
        priority="medium"
    ),
    PeptideEntry(
        rank=6, name="RP-832c", sequence="RWKFGGFK",
        structure_type="线性", target="CD206(M2巨噬细胞)",
        target_detail="CD206/MRC1 - M2型巨噬细胞标志物, IPF关键靶点",
        molecular_weight=1528.0, score_total=75.4,
        scores=[8.0, 7.5, 5.0, 7.5, 8.0, 6.0, 8.8],
        mechanism="M2巨噬细胞靶向, IPF(肺纤维化)第一管线候选",
        priority="high"
    ),
    PeptideEntry(
        rank=7, name="RPARPAR", sequence="RPARPAR",
        structure_type="线性", target="NRP-1",
        target_detail="NRP-1 CendR基序",
        molecular_weight=870.0, score_total=63.4,
        scores=[7.0, 7.0, 7.0, 6.0, 6.5, 8.5, 7.0],
        mechanism="CendR核心基序, NRP-1高亲和力",
        priority="medium"
    ),
    PeptideEntry(
        rank=8, name="MOTS-c", sequence="MRWQEMGYIFYPRKLR",
        structure_type="线性", target="线粒体",
        target_detail="线粒体衍生肽, 代谢调控",
        molecular_weight=2100.0, score_total=61.3,
        scores=[5.5, 6.5, 6.0, 6.5, 6.0, 5.5, 7.0],
        priority="low"
    ),
    PeptideEntry(
        rank=9, name="tLyP-1", sequence="CGNKRTR",
        structure_type="线性", target="NRP-1",
        target_detail="NRP-1 CendR配体",
        molecular_weight=850.0, score_total=59.3,
        scores=[6.5, 6.5, 6.0, 5.5, 6.0, 8.0, 6.5],
        priority="medium"
    ),
    PeptideEntry(
        rank=10, name="Angiopep-2", sequence="TFFYGGSRGKRNNFKTEEY",
        structure_type="线性", target="LRP1",
        target_detail="LRP1 (低密度脂蛋白受体相关蛋白1)",
        molecular_weight=2300.0, score_total=59.1,
        scores=[6.0, 6.0, 5.5, 6.0, 6.0, 5.5, 6.5],
        mechanism="BBB穿透, 脑靶向LRP1",
        priority="medium"
    ),
    PeptideEntry(
        rank=11, name="GE11", sequence="YHWYGYTPQNVI",
        structure_type="线性", target="EGFR",
        target_detail="EGFR, NSCLC(40-80% EGFR+)",
        molecular_weight=1737.0, score_total=73.6,
        scores=[8.0, 7.5, 7.0, 7.5, 7.0, 6.5, 7.5],
        mechanism="NSCLC EGFR+靶向, 患者群大",
        priority="high"
    ),
    PeptideEntry(
        rank=12, name="AKPC", sequence="KPSSPPEE",
        structure_type="线性", target="p32/gC1qR",
        target_detail="p32/gC1qR - 肿瘤/M2巨噬细胞表面",
        molecular_weight=900.0, score_total=72.8,
        scores=[6.0, 9.5, 4.0, 7.0, 6.5, 9.5, 9.0],
        mechanism="p32受体靶向, LNP修饰, ACS Nano 2024验证",
        priority="high"
    ),
    PeptideEntry(
        rank=13, name="CKRGARSTC", sequence="CKRGARSTC",
        structure_type="环肽", target="p32/gC1qR",
        target_detail="p32 - p32新配体(筛选发现)",
        molecular_weight=1124.0, score_total=82.8,
        scores=[8.5, 8.5, 8.0, 7.5, 7.5, 9.0, 8.8],
        priority="medium"
    ),
]


# ── Multi-organ database (abbreviated) ──
@dataclass
class MultiOrganEntry:
    name: str
    sequence: str
    organ_target: str
    target_receptor: str
    mechanism: str
    score: float = 0.0
    reference: str = ""

MULTI_ORGAN_DB = [
    MultiOrganEntry("iRGD", "CRGDKGPDC", "肺/肿瘤", "αvβ3+NRP-1", "CendR双靶向", 88.6),
    MultiOrganEntry("AKPC", "KPSSPPEE", "肿瘤/M2巨噬", "p32", "p32受体靶向", 72.8),
    MultiOrganEntry("Angiopep-2", "TFFYGGSRGKRNNFKTEEY", "脑", "LRP1", "BBB穿透", 59.1),
    MultiOrganEntry("GE11", "YHWYGYTPQNVI", "肺(NSCLC)", "EGFR", "EGFR靶向", 73.6),
    MultiOrganEntry("RP-832c", "RWKFGGFK", "肺(IPF)", "CD206", "M2巨噬靶向", 75.4),
    MultiOrganEntry("NGR", "CNGRC", "肿瘤血管", "CD13", "血管新生靶向", 68.4),
    MultiOrganEntry("CREKA", "CREKA", "肿瘤", "纤维蛋白", "微环境靶向", 66.5),
    MultiOrganEntry("tLyP-1", "CGNKRTR", "脑/肿瘤", "NRP-1", "CendR穿透", 59.3),
]


# ── Database class ──
class PeptideDatabase:
    """In-memory peptide database manager."""

    def __init__(self, lung_peptides: List[PeptideEntry] = None):
        self._lung = lung_peptides or LUNG_PEPTIDES_V6
        self._by_name = {p.name: p for p in self._lung}
        self._by_seq = {p.sequence: p for p in self._lung}

    # ── Lung v6 ──

    @property
    def lung_v6(self) -> List[PeptideEntry]:
        return self._lung

    def get_by_name(self, name: str) -> Optional[PeptideEntry]:
        return self._by_name.get(name)

    def get_by_sequence(self, seq: str) -> Optional[PeptideEntry]:
        return self._by_seq.get(seq)

    def search(self, query: str) -> List[PeptideEntry]:
        """Search by name, sequence, or target."""
        q = query.lower()
        results = []
        for p in self._lung:
            if (q in p.name.lower() or q in p.sequence.lower()
                    or q in p.target.lower() or q in p.target_detail.lower()):
                results.append(p)
        return results

    def top_n(self, n: int = 10) -> List[PeptideEntry]:
        return sorted(self._lung, key=lambda x: x.score_total, reverse=True)[:n]

    def by_priority(self) -> Dict[str, List[PeptideEntry]]:
        result = {"high": [], "medium": [], "low": []}
        for p in self._lung:
            result[p.priority].append(p)
        return result

    def meets_threshold(self) -> List[PeptideEntry]:
        return [p for p in self._lung if p.meets_synthesis_threshold]

    def to_dataframe(self):
        """Export to pandas DataFrame."""
        import pandas as pd
        rows = []
        for p in self._lung:
            rows.append({
                "rank": p.rank, "name": p.name, "sequence": p.sequence,
                "structure": p.structure_type, "target": p.target,
                "mw": p.molecular_weight, "score": p.score_total,
                "priority": p.priority, "mechanism": p.mechanism,
            })
        return pd.DataFrame(rows)

    def add_peptide(self, entry: PeptideEntry):
        """Add a new peptide (for wet-lab feedback)."""
        if entry.sequence in self._by_seq:
            raise ValueError(f"Sequence {entry.sequence} already exists")
        entry.rank = len(self._lung) + 1
        self._lung.append(entry)
        self._by_name[entry.name] = entry
        self._by_seq[entry.sequence] = entry

    def update_score(self, name: str, new_score: float):
        """Update score (for re-scoring)."""
        if name in self._by_name:
            self._by_name[name].score_total = new_score
