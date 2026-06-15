# ELP替代PEG的LNP设计原理

**调研日期**: 2026-05-27 | **核实更正**: 2026-05-29

## ⚠️ 文献核实更正

详见 `references/cheng-yiyun-elp-lit-verification-20260529.md`
✅ GateGuard已关闭(2026-05-29)，后续可直接写入

原文档引用的两篇程义云ELP论文经全文下载+作者核实，均不成立：
1. Adv. Sci. 2025 (Ren/Cheng) → **全文0次提到ELP/elastin**，用的是标准DMG-PEG
2. J Control Release 2025 → **作者为华中科技大学Li Fei等**，非程义云工作
3. 程义云课题组目前没有已发表的ELP替代PEG论文
4. 三个层次机制和一石三鸟设计哲学→为内部假设而非已发表文献结论

以下保留原文档的机制假设和欣肽实验数据，但注明为**内部假设（待验证）**。

## 核心洞察（内部假设，待实验验证）

ELP（弹性蛋白样多肽）替代DMG-PEG2000在LNP中的作用不仅仅是"更安全的PEG替代品"——它能**数量级地提高转染效率**。这个提升有三个层次。

## 三个机制层次

### 层次一：解决PEG的先天缺陷（安全性）

| 问题 | DMG-PEG2000 | DMG-ELP（~80aa） |
|:-----|:-----------|:----------------|
| 降解性 | ❌ 不可生物降解（体内蓄积） | ✅ 可生物降解（氨基酸） |
| 免疫原性 | ❌ 抗PEG IgM → ABC现象 | ✅ 低免疫原性（人源弹性蛋白序列） |
| 单分散性 | ❌ 多分散（PDI>1.0） | ✅ 单分散（基因编码精确分子量） |

（内部假设，待实验验证）

### 层次二：PEG Dilemma → 转染效率的"天花板"

PEG有一个已知的结构性矛盾：它延长循环时间的同时，也**抑制了细胞摄取和内体逃逸**。
- "Excessive PEGylation hinders intracellular trafficking by impeding cell endocytosis and endosomal escape" (2024文献)
- PEG水合层物理阻挡了阳离子脂质与内涵体膜的接触
- 这是PEG分子结构的固有属性，通过优化浓度无法完全解决

（内部假设，待实验验证）

### 层次三：ELP的"智能脱壳" → 转染效率数量级提升

ELP替代PEG后，转染效率的提升不仅仅是"没有了PEG的抑制作用"，而是**ELP本身主动参与**了内体逃逸过程：

1. **温敏相变（LCST行为）**
   - 循环中（37°C + 生理pH）：ELP水合伸展，"隐形" → 像PEG一样
   - 内体酸化后（pH 5-6）：ELP链中His/Glu残基质子化 → 构象变化 → 暴露出疏水区域 → 与内体膜相互作用 → **促进膜融合和mRNA释放**
   - PEG在这一步毫无贡献，ELP则主动参与

2. **内吞通路切换**
   - PEG-LNP主要走网格蛋白介导的内吞 → 溶酶体降解路径（效率低）
   - ELP修饰可以引导LNP走小窝蛋白/巨胞饮通路 → 内体逃逸效率更高

3. **增强的细胞摄取**
   - ELP的热响应性在接近细胞膜时创造了一个"粘性"更强的表面
   - 促进与细胞膜的初始接触和随后的内吞

（内部假设，待实验验证）

## 一石三鸟的设计哲学

ELP嵌合蛋白的设计理念是用一个ELP分子同时完成三件事：

| 功能 | 传统LNP实现方式 | ELP实现方式 |
|:-----|:---------------|:-----------|
| 隐形/长循环 | DMG-PEG2000（独立组分） | ELP水合层 ✅ |
| 靶向配体 | DSPE-PEG-Mal-靶向肽（多步化学合成） | ELP基因序列直接融合靶向肽 ✅ |
| 内体逃逸增强 | 依赖可电离脂质高比例（~50% SM-102） | ELP的pH响应构象变化 ✅ |

**这是最大的创新点**：不需要三个独立组分，一条ELP嵌合蛋白同时完成隐形、靶向、逃逸三个功能。

（内部假设，待实验验证）

## 实验数据（欣肽实验室）

### 2026-05-27：ELP-LNP-mRNA vs AA-LNP-mRNA

| 指标 | ELP-LNP-mRNA | AA-LNP-mRNA (DMG-PEG对照) |
|:-----|:------------|:-------------------------|
| 包封率 | 87.9% | 87.9% |
| 包封浓度 | **594 μg/ml** | 471.6 μg/ml |
| 损失率 | **22.5%** | 38.5% |

ELP组损失率降低42%（从38.5%→22.5%），是目前所有配方中的最低损失率。

### 2026-05-26：AA&ELP-LNP vs CHOL-LNP（历史参考）

| 指标 | AA&ELP联合组 | CHOL对照组 |
|:-----|:-----------|:----------|
| 包封率 | 94% | 92% |
| 损失率 | **28.4%** | 42.3% |

## 关键假设

ELP降低损失率和提高转染效率的假设机制：
1. ELP的温敏"智能壳"减少纳米粒制备过程中的聚集
2. ELP在透析过程中更好地保护mRNA不被降解
3. ELP的相变行为在浓缩步骤中减少了颗粒的不可逆聚集
4. 进入细胞后ELP的pH响应构象变化促进内体逃逸


## 参考文献

### 已核实ELP相关

- "Elastin-like peptides for efficient and safe delivery of mRNA" — J Control Release 2025, Li/Wu/Dai等，华中科技大学同济医院团队；ELP-DOTAP复合物，非LNP，非程义云工作。
- "Peptide Substitutes of PEG: Biological Outcomes on Prospective Lipid Nanoparticle Shielding Materials" — Adv. Healthcare Mater. 2025/2026, Mukthavaram et al.；PEG替代屏蔽材料方向参考，需按全文继续核实其与ELP-LNP的直接相关性。

### 非ELP但同领域参考

- 程义云课题组: faculty.ecnu.edu.cn (School of Life Sciences)；截至2026-05-29，未核实到程义云课题组已发表ELP替代PEG的LNP论文。
- "Optimization of Lipid Nanoparticles with Robust Efficiency for the Delivery of Protein Therapeutics" — Adv. Sci. 2025, Ren, Zhao, Chao, Yu, Mei, Du, Cheng；全文0次提到ELP/elastin，使用标准DMG-PEG的LNP蛋白递送论文，不应作为ELP文献引用。

### 未验证假设

- 本文"三个机制层次"、"智能脱壳"、"内吞通路切换"、"增强细胞摄取"和"一石三鸟"设计哲学均为内部机制假设，需通过Cryo-TEM、Galectin内体逃逸assay、细胞摄取/内吞通路阻断实验等验证。
