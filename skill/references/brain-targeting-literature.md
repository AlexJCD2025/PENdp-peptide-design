# 🧠 脑靶向 LNP+多肽 文献汇编（2022-2026）

> 发现于2026-05-21外部搜索。PENdp现有文献库（paper_1~7）**完全未覆盖此方向**。
> 2025-2026年为多肽-LNP脑靶向领域爆发期，建议作为下一轮文献吸收目标。

## 核心论文（直接相关）

### 1. Peptide-Functionalized LNPs for Targeted Systemic mRNA Delivery to the Brain
- **期刊**: *Nano Letters* (2025)
- **作者**: Han et al. (Mitchell Lab, UPenn)
- **核心贡献**: 设计多肽修饰LNP (pLNP) 平台，实现**系统给药→BBB穿透→脑细胞靶向**的完整流程。首次证明pLNP在全身给药后可以靶向特定脑细胞类型。
- **链接**: https://pubs.acs.org/doi/10.1021/acs.nanolett.4c05186
- **对PENdp价值**: ⭐⭐⭐⭐⭐ 最高，直接补脑靶向缺口

### 2. Peptide-Conjugated LNPs for Efficient siRNA Delivery across BBB and Treatment of GBM
- **期刊**: *ACS Chemical Biology* (2025)
- **核心贡献**: 优化**Angiopep-2修饰LNP**，实现BBB穿透（~2.23%注射剂量脑积累），GBM治疗验证。Angiopep-2肽是PENdp已有配体。
- **对PENdp价值**: ⭐⭐⭐⭐⭐ LNP+Angiopep-2的直接参考，含2.23% ID脑积累基准数据

### 3. Optimizing Angiopep-2 Density on Polymeric Nanoparticles for Enhanced BBB Penetration and GBM Targeting
- **期刊**: *Advanced Functional Materials* (2025)
- **作者**: Zhang et al.
- **核心贡献**: Angiopep-2密度对BBB穿透效率的非线性影响——**密度过高和过低都不行**，存在最优密度窗口。含in vitro/in vivo实验。
- **对PENdp价值**: ⭐⭐⭐⭐ 密度优化设计参数

### 4. KS-487: A Next-Generation Brain-Targeting Peptide Rivaling Angiopep-2
- **期刊**: *Bioconjugate Chemistry* (2025)
- **核心贡献**: 新肽KS-487在BBB穿透上**优于Angiopep-2**，选择性更强。含ICG标记体内分布成像。
- **对PENdp价值**: ⭐⭐⭐⭐ KS-487可作为新配体候选录入PENdp数据库

### 5. OS4 LNP: Lipid Nanoparticles for mRNA Delivery in Brain via Systemic Administration
- **期刊**: *Science Advances* (2025)
- **核心贡献**: 筛选获得最优LNP配方**OS4 LNP**，脑mRNA递送效率显著优于FDA批准LNP配方。
- **对PENdp价值**: ⭐⭐⭐⭐ LNP配方参考

## 综述论文

### 6. Peptide-Functionalized Nanoparticles for Brain-Targeted Therapeutics
- **期刊**: *Drug Delivery and Translational Research* (2025)
- **核心内容**: 全面综述：多肽-LNP/纳米粒子脑靶向最新进展。含配体对比表（RVG29, T7, Angiopep-2等），各类神经系统疾病应用（GBM, AD, PD, 中风等）。
- **对PENdp价值**: ⭐⭐⭐ 全景视角，表1配体对比可直接参考

### 7. Targeted Nanoparticles for Drug Delivery Across BBB in Alzheimer's Disease
- **期刊**: *PMC* (2025)
- **核心内容**: AD中的BBB靶向策略综述：转铁蛋白/ApoE模拟肽/甘露糖/双肽系统/蛋白冠调控。
- **对PENdp价值**: ⭐⭐⭐ 蛋白冠调控与PENdp的ELP-LNP设计有交叉

### 8. Revealing Angiopep-2/LRP1 Molecular Interaction for Optimal Delivery to GBM
- **期刊**: *Molecules* (2022)
- **核心内容**: Angiopep-2与LRP1受体的分子机制。含临床前+临床数据。
- **对PENdp价值**: ⭐⭐ Angiopep-2/LRP1分子机制基础文献

## 对PENdp的具体补充建议

### 可立即录入数据库的内容
1. **KS-487** — 新脑靶向肽，性能优于Angiopep-2，建议录入sequences.py的MultiOrganDB
2. **2.23% ID/g** — Angiopep-2-LNP的脑积累基准值，建议作为D12安全窗口的参考数据
3. **Angiopep-2最优密度** — AFM论文的非线性密度-BBB穿透曲线，建议融入评分系统

### 建议下一轮文献吸收管线
1. 下载 paper_A (Nano Letters pLNP) 全文 → 提取pLNP设计框架
2. 下载 paper_B (ACS Chem Bio Angiopep-2-LNP) → 提取2.23%数据+配方参数
3. 下载 paper_C (AFM密度优化) → 提取最优密度窗口
4. 综述 paper_D → 全景式配体对比表格

### 与PENdp现有管线的关系
```
脑靶向管线当前状态                              目标状态
┌──────────────────┐                        ┌──────────────────────┐
│ LRP1靶点 ✅      │                        │ LRP1靶点 ✅          │
│ TfR1靶点 ❌无肽  │   ← 吸收这些文献 →      │ TfR1靶点 ⭕ 有候选   │
│ Angiopep-2 59.1分│                        │ Angiopep-2+密度优化  │
│ tLyP-1 59.3分   │                        │ KS-487 新配体 🆕    │
│ ❌无LNP实验方案  │                        │ pLNP设计框架参照    │
│ ❌无BBB数据      │                        │ 2.23% ID基准数据    │
└──────────────────┘                        └──────────────────────┘
```
