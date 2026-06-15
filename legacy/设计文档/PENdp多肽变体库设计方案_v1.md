# PENdp多肽变体库设计方案
## 版本：v1.0 | 日期：2026-04-21 | 状态：设计完成，待验证

---

## 一、设计原则

### 1.1 核心约束
- **全部为线性序列**（环化仅作为备选）
- **保持最小功能基序**：NGR/CD13结合 + CendR/NRP-1穿透
- **侧翼残基参考文献**：ACS Combinatorial Science 2012最优序列 VLNGRME

### 1.2 评分维度（用于后续筛选）
| 维度 | 权重 | 说明 |
|------|------|------|
| CD13结合保守性 | 35% | NGR基序完整性 + 侧翼优化 |
| NRP-1结合保守性 | 25% | CendR基序 (R/K)Xammar(X)R/K |
| LNP兼容性 | 20% | 净电荷、疏水性、溶解度 |
| 血清稳定性 | 10% | 蛋白酶切割位点预测 |
| 合成可行性 | 10% | 肽长度、纯化难度 |

---

## 二、iNGR变体库（12个）

### 设计逻辑
```
原始iNGR:  CRNGRGPDC
           └─┘└────┘
           NGR   CendR (NRP-1)
```

**变异策略：**
1. **NGR侧翼优化**：参考VLNGRME（ACS 2012最优）
2. **CendR基序保持**：RNGR 或 KNGR（保持NRP-1结合）
3. **长度测试**：7-12肽

### 变体清单

| ID | 名称 | 序列 | 长度 | 变异说明 | CD13优化 | NRP-1优化 |
|----|------|------|------|----------|----------|-----------|
| NGR-01 | iNGR-原始 | **CRNGRGPDC** | 9 | 基线对照 | - | - |
| NGR-02 | iNGR-Lin | **RNGRGPDC** | 8 | 去除N端Cys | 简化 | 保持 |
| NGR-03 | VLNGR-GP | **VLNGRGPDC** | 9 | VLN侧翼 | ⭐优化 | 保持 |
| NGR-04 | VLNGR-K | **VLNGRKPDC** | 9 | VLN + CendR变体 | ⭐优化 | 变体 |
| NGR-05 | CLNGR-GP | **CLNGRGPDC** | 9 | Cys类最佳 | 优化 | 保持 |
| NGR-06 | LNGR-P | **LNGRGPDC** | 8 | 最短功能版 | 中等 | 保持 |
| NGR-07 | ALNGR-P | **ALNGRGPDC** | 9 | A类疏水侧翼 | 待测 | 保持 |
| NGR-08 | KLNGR-P | **KLNGRGPDC** | 9 | K类阳离子 | 待测 | 优化 |
| NGR-09 | SLNGR-P | **SLNGRGPDC** | 9 | S类极性侧翼 | 待测 | 保持 |
| NGR-10 | p32-NGR | **CGKRKGGGNGR** | 11 | 双靶向（p32+CD13） | 双 | 保持 |
| NGR-11 | ILNGR-P | **ILNGRGPDC** | 9 | I类疏水侧翼 | 待测 | 保持 |
| NGR-12 | iNGR长 | **CRNGRGPDCPPP** | 12 | 加长间隔 | 保持 | 降低 |

### NGR变体设计说明

```
【核心基序】
NGR基序: N---G---R (CD13结合)
CendR基序: R---N---G---R (NRP-1结合)

【侧翼残基来源】
最优侧翼(ACS 2012): V-L-NGR-M-E
                    └─疏水─└─极性

【变异原理】
1. VLNGR (NGR-03): 直接采用最优侧翼，CD13亲和力预期最高
2. CLNGR (NGR-05): Cys可形成分子内二硫键（备选环化版本）
3. LNGR (NGR-06): 最短功能版，适合空间受限的LNP表面
4. 双靶向 (NGR-10): CGKRK(p32) + GGG + NGR(CD13)，覆盖两类受体
```

---

## 三、iRGD变体库（10个）

### 设计逻辑
```
原始iRGD:  CRGDKGPDC
           └─┘└────┘
           RGD   CendR (NRP-1)
```

**变异策略：**
1. **RGD周围侧翼优化**：参考integrin结合最优残基
2. **CendR基序保持**：RGDK（蛋白酶切割后暴露CRGDK）
3. **跳过切割直接结合**：设计直接暴露CendR的版本

### 变体清单

| ID | 名称 | 序列 | 长度 | 变异说明 | Integrin优化 | NRP-1优化 |
|----|------|------|------|----------|-------------|-----------|
| RGD-01 | iRGD-原始 | **CRGDKGPDC** | 9 | 基线对照（需酶切） | - | - |
| RGD-02 | RGD-直链 | **RGDKGPDC** | 8 | 去除N端Cys | 保持 | 直接 |
| RGD-03 | RGD-K | **RGDKGPK** | 8 | 双K | 保持 | 优化 |
| RGD-04 | FRGD-SP | **FRGDSPDC** | 8 | F类疏水前导 | 优化 | 保持 |
| RGD-05 | LRGD-P | **LRGDPDC** | 8 | L类疏水 | 优化 | 简化 |
| RGD-06 | GRGD-SP | **GRGDSPDC** | 8 | G类最小 | 保持 | 保持 |
| RGD-07 | RRGD-K | **RRGDKGPDC** | 9 | 双R | 优化 | 保持 |
| RGD-08 | iRGD类 | **CRGDKPPC** | 8 | 跳过酶切 | 保持 | 直接 |
| RGD-09 | FRGD-K | **FRGDKGPDC** | 9 | 综合优化 | ⭐优化 | 保持 |
| RGD-10 | PRGD-K | **PRGDKGPDC** | 9 | P类（稳定性） | 待测 | 保持 |

### RGD变体设计说明

```
【核心基序】
RGD基序: R---G---D (Integrin αvβ3结合)
CendR基序: RGDK → 蛋白酶切割 → CRGDK → NRP-1结合

【设计原理】
1. 直接CendR (RGD-02/03/08): 不依赖酶切，直接暴露NRP-1结合位点
   - 适合LNP系统（LNP表面可能缺乏足量的目标蛋白酶）
2. 疏水侧翼 (RGD-04/05): 纤维蛋白源序列参考，增强Integrin亲和力
3. 双R (RGD-07): Arg双体增强Integrin结合（文献支持）

【关键文献】
- ACS JCIM 2023: iRGD与Integrin结合的分子动力学模拟
- 疏水残基(F/L)位于RGD前方可增强Integrin αvβ3亲和力
```

---

## 四、融合型变体库（4个）

### 设计逻辑
同时包含NGR（CD13）和RGD（Integrin）两种靶向基序，实现"双锚定"策略。

| ID | 名称 | 序列 | 长度 | 说明 |
|----|------|------|------|------|
| FUS-01 | NGR+RGD | **CNGRGGGRGD** | 10 | NGR+RGD串联 |
| FUS-02 | 双靶向1 | **VLNGRGGFRGD** | 11 | 优化侧翼双基序 |
| FUS-03 | 短双靶向 | **LNGRGGRGD** | 9 | 最短双靶向 |
| FUS-04 | iNGR-iRGD | **CRNGRCRGD** | 9 | 混合型 |

**融合型注意事项：**
- 两个基序可能产生空间干扰
- 需要较长的间隔序列(GGG/PPP)
- CD13和Integrin的共表达可能增强肿瘤靶向

---

## 五、汇总表

| 系列 | 变体数 | 优先级 |
|------|--------|--------|
| iNGR系列 | 12个 | ⭐⭐⭐ 最高 |
| iRGD系列 | 10个 | ⭐⭐ 高 |
| 融合型 | 4个 | ⭐ 探索性 |
| **合计** | **26个** | |

---

## 六、筛选计划

### 第一轮：计算机筛选（优先级排序）
1. **AlphaFold3**预测所有26个变体的3D结构
2. 预测CD13（PDB参考）和NRP-1（PDB参考）的结合模式
3. 给出初步亲和力评分

### 第二轮：湿实验验证（Top 10候选）
1. CD13结合实验（HT-1080细胞，流式）
2. NRP-1结合实验（ 경쟁细胞）
3. 血清稳定性测试（24h）

### 第三轮：LNP功能验证（Top 5候选）
1. LNP修饰（DSPE-PEG2000-肽）
2. 粒径/电位表征
3. 细胞摄取实验（A549肺癌细胞）
4. 动物靶向分布（裸鼠）

---

## 七、序列文件（供合成）

### 7.1 iNGR系列（12条）
```
>NGR-01|iNGR-原始|CYS-R-N-G-R-G-P-D-C
>NGR-02|iNGR-Lin|R-N-G-R-G-P-D-C
>NGR-03|VLNGR-GP|V-L-N-G-R-G-P-D-C
>NGR-04|VLNGR-K|V-L-N-G-R-K-P-D-C
>NGR-05|CLNGR-GP|C-L-N-G-R-G-P-D-C
>NGR-06|LNGR-P|L-N-G-R-G-P-D-C
>NGR-07|ALNGR-P|A-L-N-G-R-G-P-D-C
>NGR-08|KLNGR-P|K-L-N-G-R-G-P-D-C
>NGR-09|SLNGR-P|S-L-N-G-R-G-P-D-C
>NGR-10|p32-NGR|C-G-K-R-K-G-G-G-N-G-R
>NGR-11|ILNGR-P|I-L-N-G-R-G-P-D-C
>NGR-12|iNGR长|C-R-N-G-R-G-P-D-C-P-P-P
```

### 7.2 iRGD系列（10条）
```
>RGD-01|iRGD-原始|C-R-G-D-K-G-P-D-C
>RGD-02|RGD-直链|R-G-D-K-G-P-D-C
>RGD-03|RGD-K|R-G-D-K-G-P-K
>RGD-04|FRGD-SP|F-R-G-D-S-P-D-C
>RGD-05|LRGD-P|L-R-G-D-P-D-C
>RGD-06|GRGD-SP|G-R-G-D-S-P-D-C
>RGD-07|RRGD-K|R-R-G-D-K-G-P-D-C
>RGD-08|iRGD类|C-R-G-D-K-P-P-C
>RGD-09|FRGD-K|F-R-G-D-K-G-P-D-C
>RGD-10|PRGD-K|P-R-G-D-K-G-P-D-C
```

### 7.3 融合型（4条）
```
>FUS-01|NGR+RGD|C-N-G-R-G-G-G-R-G-D
>FUS-02|双靶向1|V-L-N-G-R-G-G-F-R-G-D
>FUS-03|短双靶向|L-N-G-R-G-G-R-G-D
>FUS-04|iNGR-iRGD|C-R-N-G-R-C-R-G-D
```

---

*设计文件状态：待AlphaFold结构预测验证*
*合成建议：先合成iNGR系列（NGR-01至NGR-05）和iRGD系列（RGD-01至RGD-05）共10条*
