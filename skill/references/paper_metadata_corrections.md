# PENdp 文献元数据修正记录

## 背景
2026-05-13 对 7 篇论文进行全文本抓取时发现原有 papers.py 中的元数据有 3 处错误。以下为详细修正记录。

---

## 修正 1: AKPC 论文 (Paper 3)

### 原数据 (papers.py v1)
| 字段 | 值 |
|:-----|:----|
| 标题 | AKPC-modified LNP for p32-targeted delivery |
| 作者 | — |
| 来源 | ACS Nano |
| 年份 | 2024 |
| DOI | (无) |
| 靶点 | p32 |

### 实际数据 (全文验证)
| 字段 | 值 |
|:-----|:----|
| 标题 | Peptide-Modified Lipid Nanoparticles Boost the Antitumor Efficacy of RNA Therapeutics |
| 作者 | Zhao et al. |
| 来源 | ACS Nano 2025, 19(14), 13685-13704 |
| 年份 | **2025** |
| DOI | 10.1021/acsnano.4c14625 |
| PMID | 40176316 |
| PMC ID | PMC12004924 |
| 靶点 | **CD44** (不是 p32) |
| 多肽 | A6 (KPSSPPEE), 非AKPC/LinTT1 |
| LNP命名 | AKPC-LNP (A6-KPSSPPEE-Cholesterol-PEG4-GGGKKKGK) |

### 影响
- PENdp 数据库中 KPSSPPEE 的靶点从 p32 → CD44 已修正
- iRGD (CRGDKGPDC, αvβ3/αvβ5) 和 AKPC (KPSSPPEE, CD44) 靶点不同，说明数据库的靶向冗余还需要重新评估
- 年份从2024→2025说明是刚发表的论文，时效性没问题

---

## 修正 2: MOLEA 论文 (Paper 5)

### 原数据
| 字段 | 值 |
|:-----|:----|
| 标题 | MOLEA: Multi-Objective Optimization for LNP Design |
| 作者 | Bowen Li Lab |
| 来源 | bioRxiv / GitHub |
| 年份 | 2025 |

### 实际数据
| 字段 | 值 |
|:-----|:----|
| 标题 | A multiobjective AI model for LNP engineering enhances tissue-selective mRNA delivery |
| 作者 | Muye Zhou, Yue Xu, Gen Li et al. (Bowen Li Lab) |
| 来源 | **Nature Biotechnology, 2026** |
| 年份 | **2026** |
| DOI | 10.1038/s41587-026-03109-0 |

### 影响
- 已发表在 Nature Biotech 而非 bioRxiv — 说明团队认可度高
- 年份2026说明这是刚发表的新成果
- 公开代码: bowenli-lab/MOLEA (GitHub)

---

## 修正 3: ASSET Protocol (Paper 6)

### 原数据
| 字段 | 值 |
|:-----|:----|
| 标题 | ASSET Protocol: Antibody-directed LNP |
| 作者 | — |
| 来源 | — |
| 年份 | 2025 |

### 实际数据
| 字段 | 值 |
|:-----|:----|
| 标题 | Cell specific delivery of modified mRNA expressing therapeutic proteins to leukocytes |
| 作者 | Veiga N, Goldsmith M, Granot Y, et al. (Peer Lab, Tel Aviv) |
| 来源 | **Nature Communications, 2018, 9:4493** |
| 年份 | **2018** |
| DOI | 10.1038/s41467-018-06936-1 |

### 影响
- ASSET 实际上是经典论文 (2018), 不是新成果
- 2025年有改进版 (TP1107, Chen et al. Nature Nanotech 2025)
- D9评分维度应引用2018年原始论文 + 2025年改进版

---

## 限制

- Paper 1 (The landscape for therapeutic cancer vaccines): Nature paywall, 无开放版
- 已获取全文的论文存储在 `~/.hermes/workspace/PENdp/pendp/literature/texts/`
