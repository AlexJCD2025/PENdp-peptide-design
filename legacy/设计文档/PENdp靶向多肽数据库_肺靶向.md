# 🫁 PENdp 肺靶向多肽数据库

*建立：2026-04-17 | v5 | 21条序列 | 来源：文献调研+AI验证*

---

## 一、靶点家族总览

| 家族 | 代表多肽 | 靶点 | 机制 |PENdp优先级 |
|------|---------|------|------|-----------|
| **iRGD家族** | iRGD(KD), iNGR | αvβ3/β5 + NRP-1 | CendR通路→跨内皮穿透 | ⭐⭐⭐⭐⭐ |
| **p32/gC1qR** | AKPC, LinTT1, CKRGARSTC | p32受体 | 肿瘤/巨噬细胞靶向 | ⭐⭐⭐⭐⭐ |
| **NRP-1** | RPARPAR, tLyP-1 | NRP-1 | CendR通路穿透 | ⭐⭐⭐⭐ |
| **NGR/CD13** | NGR, iNGR | CD13氨肽酶N | 肿瘤血管新生 | ⭐⭐⭐⭐ |
| **EGFR** | GE11 | EGFR | NSCLC高表达 | ⭐⭐⭐⭐ |
| **CD206/M2** | RP-832c | CD206 | 肺纤维化/巨噬 | ⭐⭐⭐⭐ |
| **纤维蛋白** | CREKA | 凝血级联 | 肺转移灶 | ⭐⭐⭐ |

---

## 二、完整序列数据库 v5

| # | 名称 | 完整序列 | MW(Da) | 关键靶向基序 | 总分 |
|---|------|---------|---------|------------|------|
| 1 | **iRGD(KD)⭐** | CRGDKGPDC | 1093 | RGD+CendR双基序 | **70.2** |
| 2 | iRGD-L⭐ | CRGDK | 649 | RGD+CendR | 69.3 |
| 3 | NGR | CNGRC | 623 | NGR(CD13) | 69.2 |
| 4 | **iNGR⭐** | CRNGRGPDC | 1120 | NGR+CendR双靶向 | **68.5** |
| 5 | CKRGARSTC | CKRGARSTC | 1124 | p32新配体 | 65.8 |
| 6 | NGR-L | CNGR | 502 | NGR(CD13) | 63.9 |
| 7 | LyP-1 | CGNKRTRGC | 1137 | p32+NRP-1 | 62.7 |
| 8 | CREKA | CREKA | 677 | 纤维蛋白 | 61.5 |
| 9 | LinTT1⭐ | AKRGARSTA | 1060 | p32+uPA激活 | 59.8 |
| 10 | RPARPAR⭐ | RPARPAR | 930 | NRP-1(CendR) | 59.8 |
| 11 | AKPC⭐ | AKPC | 471 | p32 | 58.4 |
| 12 | RP-832c⭐ | RWKFGGFKWR | 1528 | CD206(M2巨噬) | 57.5 |
| 13 | RGD | RGD | 382 | αvβ3/β5 | 57.2 |
| 14 | MOTS-c | MRWQEMGYIFYPRKLR | 2442 | 线粒体 | 56.9 |
| 15 | tLyP-1(7肽)⭐ | CGNKRTR | 941 | NRP-1+p32 | 54.8 |
| 16 | GE11⭐ | YHWYGYTPQNVI | 1737 | EGFR(NSCLC) | 53.4 |
| 17 | F3 | KDEPQRRSARLSAKPAPPKPEPKPKKAPAKK | 3969 | Nucleolin | 32.6 |

⭐ = PENdp平台重点关注

---

## 三、核心多肽详解

### 3.1 iRGD(KD) ⭐⭐⭐⭐⭐（最高优先级）

**序列**：H-Cys-Arg-Gly-Asp-Lys-Gly-Pro-Asp-Cys-OH（环肽）
**分子量**：1093.2 Da
**靶点**：αvβ3/αvβ5整合素 + NRP-1（神经菌毛蛋白-1）

**CendR双重靶向机制**：
```
Step 1: RGD → 结合αvβ3/αvβ5（肿瘤/肺血管内皮高表达）
Step 2: K → 被肿瘤微环境中protease（ MMP/furin）切割
Step 3: 暴露 CendR motif (R→PARPAR)
Step 4: CendR → 高亲和力结合NRP-1
Step 5: NRP-1 → 跨内皮转运 + 肿瘤深部穿透
Step 6: 进入肿瘤细胞
```

**iRGD变体说明**：
| 变体 | 序列 | 差异 |
|------|------|------|
| iRGD(KD) | CRGDKGPDC | K被切割→暴露CendR（标准版） |
| iRGD(RD) | CRGDRGPDC | R被切割（等效） |
| iRGDD | CRGDDGPDC | D不能被切割→失去CendR功能 |
| iRGD-L | CRGDK | 线性版本，无环→稳定性略低 |
| iNGR | CRNGRGPDC | NGR替代RGD→同时靶向CD13+NRP-1（双靶向） |

---

### 3.2 iNGR（双靶向新星）⭐⭐⭐⭐⭐

**序列**：H-Cys-Arg-Asn-Gly-Arg-Gly-Pro-Asp-Cys-OH
**分子量**：1120.2 Da
**靶点**：CD13（肿瘤血管）+ NRP-1（CendR穿透）= **双靶向**

**iNGR vs iRGD的区别**：
- iRGD：RGD基序→αvβ3/β5整合素
- iNGR：NGR基序→CD13/氨肽酶N（肿瘤新生血管内皮）

**为什么PENdp应该优先考虑iNGR？**
- CD13在肿瘤血管内皮高表达
- 积雪草酸+ELP-LNP本身有膜融合增强
- iNGR双靶向=血管识别+穿透，一步到位

---

### 3.3 p32/gC1qR家族（新发现，重要）

**p32受体**：线粒体/细胞表面蛋白，在肿瘤细胞和M2巨噬细胞高表达

| 多肽 | 序列 | 特点 |
|------|------|------|
| **AKPC** | AKPC | 471Da，最小p32配体，LNP修饰专用 |
| **LinTT1** | AKRGARSTA | TT1线性版，uPA激活→CendR→NRP-1 |
| **CKRGARSTC** | CKRGARSTC | 新发现p32配体，RGAR基序 |

**AKPC（ACS Nano 2024）**：专门验证用于LNP修饰，直接增强细胞摄取

---

### 3.4 GE11（EGFR靶向）⭐⭐⭐⭐

**序列**：Tyr-His-Trp-Tyr-Gly-Tyr-Thr-Pro-Gln-Asn-Val-Ile（12肽）
**靶点**：EGFR（NSCLC高表达，40-80%）
**优势**：无免疫原性，比西妥昔单抗小，肿瘤穿透性更好

---

### 3.5 RP-832c（肺纤维化新方向）⭐⭐⭐⭐

**序列**：H-Arg-Trp-Lys-Phe-Gly-Gly-Phe-Lys-Trp-Arg-OH（10肽）
**靶点**：CD206/M2型巨噬细胞
**应用**：肺纤维化（非肿瘤）
**为什么重要**：积雪草酸+ELP平台的核酸药物可以靶向M2巨噬细胞，治疗肺纤维化

---

## 四、PENdp平台多肽修饰策略

### 4.1 积雪草酸+ELP-LNP + 多肽靶向 = 完整方案

```
积雪草酸（增强膜融合）
    ↓
ELP（弹性蛋白样多肽，形成蛋白冠）
    ↓
多肽配体（表面修饰）
    ↓
    ├─ iRGD/iNGR → 肿瘤血管+穿透
    ├─ AKPC/LinTT1 → p32+肿瘤/M2巨噬
    ├─ GE11 → NSCLC(EGFR+)
    └─ RP-832c → 肺纤维化(M2)
```

### 4.2 蛋白冠协同假说

```
ELP表面
    ↓ 吸附血清蛋白
蛋白冠形成（富Arg/Lys序列促进）
    ↓
多肽配体 + 蛋白冠协同识别
    ↓
受体介导内吞（CD44/p32/NRP-1/EGFR）
    ↓
积雪草酸增强膜融合 → 核酸胞内释放
```

---

## 五、AI Pipeline说明

**文件**：`/Volumes/Jarvis的资料盘/PeptideAI/lung_peptide_ranking_v5.csv`
**模型**：ESM-2 8M（MPS/Mac mini GPU）
**评分维度**：
- 靶向基序(35%)：RGD/NGR/CendR等已知基序
- 物化性质(22.5%)：MW/GRAVY/pI
- LNP兼容性(18%)：环化/Cys/电荷
- 蛋白冠形成(18%)：两亲性/电荷/Pro-Gly
- ESM结构相似度(6.5%)：以iRGD为参考

---

## 六、下一步行动

### 立即（1-2周）
1. **湿实验验证首选序列**：iRGD(KD)、iNGR、AKPC
   - 合成3条多肽
   - 修饰LNP（DSPC/胆固醇/积雪草酸/ELP/多肽-PEG2000）
   - 测细胞摄取（A549肺癌细胞）
   
2. **补充p32结合数据**：测AKPC、LinTT1、CKRGARSTC的Kd值

### 短期（1-2月）
3. 动物靶向分布验证（i.v.注射→肺/肝/脾分布）
4. 积雪草酸浓度优化（0-50mol%）

### 中期（3-6月）
5. 建立自己的靶向肽-受体亲和力数据库
6. 微调AI预测模型

---

## 七、关键参考文献

1. **iRGD CendR机制**：PMC11592346（2024）
2. **iNGR双靶向**：Mol Ther. 2019（iNGR: CRNGRGPDC）
3. **AKPC LNP修饰**：ACS Nano 2024（10.1021/acsnano.4c14625）
4. **LinTT1 p32**：ACS Pharmacol Transl Sci 2022
5. **GE11 EGFR**：PMC5874815
6. **RP-832c CD206**：PMC10177262（肺纤维化）
7. **tLyP-1 p32**：PubMed 36332316
8. **CendR/NRP-1通路**：Front Oncol 2013
9. **LNP多肽修饰2024**：ACS Nano 2024（10.1021/acsnano.4c18636）
10. **肿瘤归巢多肽**：ACS Pharmacol Transl Sci（10.1021/acsptsci.5c00241）
