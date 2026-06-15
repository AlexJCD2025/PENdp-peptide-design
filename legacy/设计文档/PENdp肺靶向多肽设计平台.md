# 🫁 PENdp 肺靶向多肽设计平台

*项目启动：2026-04-17 | 欣肽生物 AI驱动药物递送平台*

---

## 一、项目背景

### 1.1 PENdp 平台定位

**PENdp = 积雪草酸 + ELP 新型纳米脂质体核酸递送平台**

```
积雪草酸（Asiaticoside）
    ↓ 替代传统胆固醇
增强LNP膜融合能力
    ↓
ELP（弹性蛋白样多肽）
    ↓ 形成蛋白冠（protein corona）
通过细胞表面受体结合 → 受体介导内吞
    ↓
精准递送核酸药物至目标器官/细胞
```

### 1.2 ELP 的核心机制

| 机制 | 说明 |
|------|------|
| **蛋白冠形成** | ELP表面吸附宿主蛋白形成"冠"，被细胞受体识别 |
| **受体介导内吞** | 蛋白冠-受体结合 → 精准内吞（非被动胞吞） |
| **温敏特性** | ELP有inverse phase transition（升温析出），可热靶向 |

### 1.3 多肽表面修饰的增量价值

```
积雪草酸+ELP-LNP（基础颗粒）
    ↓ 表面修饰靶向多肽
+ iRGD/iNGR → αvβ3/NRP-1 → 肺肿瘤血管+穿透
+ A6(CD44) → 肿瘤干细胞+耐药细胞
+ GE11(EGFR) → NSCLC(非小细胞肺癌)
+ RP-832c(CD206) → M2巨噬细胞→肺纤维化
```

---

## 二、AI平台架构

### 2.1 技术栈

| 组件 | 工具 | 位置 |
|------|------|------|
| Python环境 | Python 3.11 + venv | `/Volumes/Jarvis的资料盘/PeptideAI/peptide_venv` |
| 结构预测 | ESM-2 8M (MPS/GPU) | Apple Silicon GPU加速 |
| 序列评分 | 自建评分函数 | `peptide_lung_pipeline.py` |
| 知识库 | Markdown + Obsidian | Obsidian wiki |
| 数据管理 | CSV + Pickle | `lung_peptide_ranking_v5.csv` |

### 2.2 评分体系（五维加权）

```
综合评分 = 靶向基序(35%) + 物化性质(22.5%) + LNP兼容性(18%) + 蛋白冠形成(18%) + ESM结构相似度(6.5%)
```

**靶向基序（35%）**：RGD/NGR/CendR/iNGR等已知靶向基序
**物化性质（22.5%）**：MW/GRAVY/pI/序列长度
**LNP兼容性（18%）**：环化/Cys/电荷/疏水性
**蛋白冠形成（18%）**：两亲性/电荷/Pro-Gly含量
**ESM结构相似度（6.5%）**：以iRGD为参考的ESM-2 8M embedding余弦相似度

---

## 三、核心靶点家族

| 家族 | 代表多肽 | 靶点 | PENdp优先级 |
|------|---------|------|-----------|
| **iRGD家族** | iRGD(KD), iNGR | αvβ3/β5 + NRP-1 | ⭐⭐⭐⭐⭐ |
| **p32/gC1qR** | A6, LinTT1, CKRGARSTC | p32受体 | ⭐⭐⭐⭐⭐ |
| **NRP-1** | RPARPAR, tLyP-1 | NRP-1(CendR通路) | ⭐⭐⭐⭐ |
| **NGR/CD13** | NGR, iNGR | CD13(氨肽酶N) | ⭐⭐⭐⭐ |
| **EGFR** | GE11 | EGFR(NSCLC) | ⭐⭐⭐⭐ |
| **CD206/M2** | RP-832c | CD206(M2巨噬) | ⭐⭐⭐⭐ |
| **纤维蛋白** | CREKA | 凝血级联 | ⭐⭐⭐ |

---

## 四、Top 5 推荐序列

| # | 名称 | 序列 | MW(Da) | 靶点 | 总分 |
|---|------|------|---------|------|------|
| 1 | **iRGD(KD)** | CRGDKGPDC | 1093 | αvβ3/β5+NRP-1 | 70.2 |
| 2 | iRGD-L | CRGDK | 649 | αvβ3/β5+NRP-1 | 69.3 |
| 3 | NGR | CNGRC | 623 | CD13 | 69.2 |
| 4 | **iNGR** | CRNGRGPDC | 1120 | CD13+NRP-1 | 68.5 |
| 5 | iRGD(RD) | CRGDRGPDC | 1121 | αvβ3/β5+NRP-1 | 66.4 |

⭐ **iNGR（CRNGRGPDC）是全新双靶向方案**

---

## 五、下一步行动计划

### 立即（1-2周）
- [ ] 湿实验验证首选序列：iRGD(KD)、iNGR
- [ ] 合成多肽（GMP级SPPS）
- [ ] LNP制备（积雪草酸/DSPC/胆固醇/ELP/多肽-PEG2000）
- [ ] 细胞摄取实验（A549肺癌细胞 vs 对照）

### 短期（1-2月）
- [ ] 动物靶向分布（i.v.→肺/肝/脾）
- [ ]积雪草酸浓度梯度优化
- [ ] 补充p32受体结合数据

### 中期（3-6月）
- [ ] 建立内部靶向肽-受体亲和力数据库
- [ ] 微调ESM-2或训练属性预测模型
- [ ] "设计→预测→合成→验证"闭环

---

## 六、关键文件索引

| 文件 | 说明 |
|------|------|
| `knowledge/01_生物医药/PENdp靶向多肽数据库_肺靶向.md` | 完整序列数据库v5（21条） |
| `knowledge/01_生物医药/化学合成多肽原料企标参考框架_20260414.md` | SPPS合成工艺参考 |
| `/Volumes/Jarvis的资料盘/PeptideAI/lung_peptide_ranking_v5.csv` | 评分结果数据 |
| `/Volumes/Jarvis的资料盘/PeptideAI/peptide_lung_pipeline.py` | AI评分Pipeline脚本 |
| `/Volumes/Jarvis的资料盘/PeptideAI/peptide_embeddings_8M.pkl` | ESM-2 8M embedding |

---

## 七、关键文献

1. **iRGD CendR机制**：PMC11592346（2024）
2. **iNGR双靶向**：Mol Ther. 2019
3. **A6(CD44)LNP修饰**：ACS Nano 2024（10.1021/acsnano.4c14625）
4. **LinTT1 p32**：ACS Pharmacol Transl Sci 2022
5. **GE11 EGFR**：PMC5874815
6. **RP-832c CD206**：PMC10177262
7. **LNP多肽修饰2024**：ACS Nano 2024（10.1021/acsnano.4c18636）
8. **积雪草酸LNP**：参考欣肽内部数据

---

*本项目由Jarvis AI辅助驱动 | 2026-04-17*
