# PENdp肺靶向多肽设计逻辑重构
## 阶段小结 v1.0
**日期：2026-04-21 | 状态：进行中**

---

## 一、核心决策

### 1.1 设计理念转变
- **旧路径**：基于评分的排名筛选（4月17日方法）
- **新路径**：**基础研究 → 逻辑推导 → 设计原则 → 结构验证 → 实验验证**

### 1.2 多肽设计与积雪草酸的关系
- **澄清**：多肽修饰 ≠ 积雪草酸
- **积雪草酸 (AA)**：替代胆固醇，增强LNP膜融合（独立模块）
- **多肽表面修饰**：受体介导靶向 + 组织穿透（独立模块）
- **结论**：两个设计维度独立，无需"结合"设计

### 1.3 线性 > 环化（针对LNP系统）
| 维度 | 线性 | 环化 | LNP适用性 |
|------|------|------|-----------|
| 合成 | 简单 | 复杂 | ✅ 线性更优 |
| 稳定性 | 高 | NGR→isoDGR转化 | ✅ 线性更稳定 |
| 亲和力 | 中等 | 更高 | 需通过侧翼优化弥补 |

---

## 二、受体亲和力数据库（已验证数据）

### 2.1 受体-配体亲和力总览

| 受体 | 配体 | 序列 | 亲和力 | 等级 | 文献 |
|------|------|------|--------|------|------|
| **Integrin αvβ3** | c(RGD)₂ | c(RGDyK)₂ | Kd = **3.87 nM** | 非常高 | PubMed 2017 |
| **CD13** | 环化NGR | c(NGR) | IC50 ≈ **75 nM** | 高 | PMC6271277 |
| **p32/gC1qR** | CGKRK | CGKRK | Kd = **400 nM** | 中高 | PMC3863797 |
| **NRP-1 (CendR)** | tLyP-1 | CGNKRTR | IC50 = **4,000 nM** | 中等 | MedChemExpress |

### 2.2 iRGD vs iNGR vs iNGR 详细对比

| 特性 | iRGD | iNGR |
|------|------|------|
| **第一步（锚定）** | Integrin αvβ3 (Kd ≈ 4 nM) | CD13 (IC50 ≈ 75 nM) |
| **第二步（穿透）** | 蛋白酶激活 → CendR → NRP-1 | 直接CendR → NRP-1 |
| **激活方式** | 肿瘤微环境酶激活（被动） | 顺序结合（主动） |
| **肿瘤特异性** | 中等 | 可能更高（CD13在肿瘤血管高表达） |
| **LNP适用性** | 需酶切割，可能受限 | 直接结合，**更适合LNP** |
| **产业化** | ✅ Certepetide (Lisata, Phase II) | ❌ 仅临床前 |
| **竞争格局** | 已商业化 | 差异化空间大 |

### 2.3 关键结论：iNGR的双靶向机制（已验证）

**假设验证：✅ 成立**

文献来源：*De Novo Design of a Tumor-Penetrating Peptide* (Cancer Research, 2013, PMC3548935)

> "The tumor-homing motif in the new peptide is the **NGR sequence, which binds to endothelial CD13**. The NGR sequence was placed in the context of a CendR motif (RNGR), and this sequence was embedded in the iRGD framework. The resulting peptide (CRNGRGPDC, **iNGR**) homed to tumor vessels and **penetrated**..."

**两步机制确认：**
```
步骤1️⃣ 【锚定】NGR → CD13（肿瘤血管内皮）
         KD ≈ 75 nM
         作用：富集在肿瘤血管壁

步骤2️⃣ 【穿透】CendR (RNGR) → NRP-1 → 触发细胞穿透
         IC50 ≈ 4 μM
         作用：介导跨血管壁/组织穿透，进入肿瘤实质
```

---

## 三、关键研究发现

### 3.1 NGR侧翼残基的决定性作用

**文献**：ACS Combinatorial Science (2012, PMID: 23030271)
**发现**：45种不同侧翼序列的NGR多肽阵列筛选

| 序列 | 类型 | CD13结合 |
|------|------|----------|
| 标准NGR | CNGRC | 中等（基线） |
| **c(VLNGRME)C** | 环化 | **最高**（最优） |
| c(CNGRC) | 环化 | 较低 |

**关键洞察**：侧翼残基对CD13亲和力有决定性影响，VLNGRME类序列（类纤维连接蛋白）显著优于标准NGR。

### 3.2 NGR → isoDGR 转化问题（针对环化肽）

**文献**：JBC (2010, PMID: 20047162)
**发现**：
- 环化NGR肽随时间发生 **NGR → isoDGR** 化学转化
- isoDGR从CD13结合转为结合Integrin αvβ3
- 这是一个**受体切换（receptor switching）**现象

**对LNP设计的意义**：
- 线性NGR更稳定，避免此转化问题
- 环化NGR可能产生非预期靶向

### 3.3 A6肽的靶点澄清

**重要纠正**：

| 肽 | 靶点 | 序列 | 原笔记错误 |
|----|------|------|-----------|
| A6 | **CD44**（非p32！） | Ac-KPSSPPEE-NH2 | ❌ 之前标记为p32 |
| CGKRK | p32/gC1qR | CGKRK | ✅ 正确 |

**临床应用**：A6肽已有临床试验数据（抗转移），AKPC-LNP (ACS Nano 2024)已验证CD44靶向LNP。

---

## 四、产业化与临床验证

### 4.1 iRGD：Certepetide (LSTA1)

| 项目 | 信息 |
|------|------|
| **公司** | Lisata Therapeutics (NASDAQ: LSTA) |
| **发明人** | Dr. E. Ruoslahti (DrugCendR Inc.) |
| **临床阶段** | **Phase II**（转移性胰腺癌） |
| **最新数据** | 2025年1月：令人鼓舞的初步疗效数据 |
| **试验** | ASCEND (Phase II), iLSTA (Phase 1b/2a) |

### 4.2 iNGR：仅临床前

- 发表：胶质母细胞瘤动物模型（PubMed: 28388081, 2017）
- 结论：iNGR修饰脂质体比非修饰组有更强的肿瘤血管靶向和穿透
- 尚无企业商业化

---

## 五、设计决策

### 5.1 当前决策

1. ✅ 多肽设计与积雪草酸独立
2. ✅ 线性 > 环化（LNP场景）
3. ✅ 两个靶点（iRGD + iNGR）都需优化
4. ✅ iNGR作为主要候选（差异化 + LNP适用性）

### 5.2 待决策

- [ ] iNGR vs iRGD 最终二选一（需变体库数据）
- [ ] 具体侧翼序列优化方案
- [ ] 变体库规模与优先级

---

## 六、下一步工作

### 6.1 阶段一：变体库设计（进行中）
- 设计10-20个侧翼序列变体
- 覆盖iRGD和iNGR两个系列
- 基于文献数据进行优先级排序

### 6.2 阶段二：计算机筛选
- AlphaFold3 / ESM-3 结构预测
- 预测CD13/NRP-1结合口袋相互作用
- 筛选5-10个高优先级候选

### 6.3 阶段三：湿实验验证
- CD13结合实验（HT-1080细胞）
- NRP-1结合实验
- LNP修饰后的粒径/电位表征
- 动物靶向分布实验

---

## 七、核心文献索引

| # | 文献 | 关键内容 |
|---|------|----------|
| 1 | PMC3548935 (Cancer Research 2013) | iNGR两步机制证明 |
| 2 | ACS Combinatorial Science 2012 | NGR侧翼序列优化，cVLNGRME最优 |
| 3 | PMC6271277 (Mol Pharm 2018) | 环化NGR IC50 = 75 nM |
| 4 | JBC 2010 | NGR→isoDGR转化问题 |
| 5 | PMC5461880 (2017) | NRP-1介导的肿瘤穿透综述 |
| 6 | Lisata Therapeutics (2025) | Certepetide Phase II临床数据 |
| 7 | ACS Nano 2024 | AKPC-LNP (CD44靶向) |
| 8 | PMC3863797 | CGKRK-p32系统，Kd = 400 nM |

---

*文档状态：待补充变体库设计和AlphaFold预测结果*
*下次更新：变体库设计方案完成后*
