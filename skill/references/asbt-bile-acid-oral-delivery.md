# ASBT/胆汁酸通路口服多肽递送 — 文献与机制概述

> 2026-05-22 | 来源: Web搜索 | 欣肽生物ASBT-PLGA项目背景调研

## 一、ASBT (SLC10A2) 生物学

### 生理功能
- **全称**: Apical Sodium-Dependent Bile Acid Transporter (顶端钠依赖性胆汁酸转运体)
- **表达位置**: 回肠末端（ileum）肠上皮细胞**顶膜**
- **生理角色**: 负责肠道胆汁酸重吸收的**95%** → 维持肠肝循环（enterohepatic circulation）
- **底物**: 结合型胆汁酸（甘氨胆酸GCA、牛磺胆酸TCA等）
- **转运机制**: Na⁺偶联共转运，2 Na⁺ : 1 胆汁酸分子

### 为什么适合药物递送
- 高表达、高吞吐量（每天回收~20g胆汁酸）
- 回肠定位 → 避开胃酸/十二指肠酶降解
- 天然内源性通路 → 免疫原性风险低
- 已证明可承载分子量高达~1kDa的偶联物

### ASBT vs PepT1 的区别（重要！）

| 特性 | ASBT (SLC10A2) | PepT1 (SLC15A1) |
|:----|:---------------|:----------------|
| **表达部位** | 回肠末端 | 十二指肠/空肠为主 |
| **天然底物** | 结合型胆汁酸 | 二肽/三肽 |
| **转运机制** | Na⁺依赖共转运 | H⁺依赖共转运 |
| **已验证载药** | 胆酸偶联前药、胆酸修饰纳米粒 | 氨基酸/肽前药偶联 |
| **代表性药物** | 无已上市口服肽（研发中） | 伐昔洛韦（前药） |

## 二、ASBT靶向口服递送的三种策略

### 策略1: 前药偶联 (Prodrug Conjugation)
- 将药物共价偶联到胆汁酸上
- 通过ASBT吸收进入肠上皮细胞
- 在细胞内或入血后释放活性药物
- **限制**: 载药量≈1:1（1分子药/1分子胆酸），不适合大分子

### 策略2: 胆酸修饰纳米载体 (Bile Acid-Modified Nanocarriers)
- 在纳米颗粒表面偶联胆酸/脱氧胆酸
- 纳米颗粒通过ASBT介导内吞进入细胞
- **核心论文**:
  - **15.9% Bioav (胰岛素)**: 脱氧胆酸修饰壳聚糖纳米粒, Biomaterials 2017, PMID: 28756365
  - **19.5% Bioav (Exendin-4)**: 甘氨胆酸-壳聚糖包裹脂质体, J Control Release 2020, PMID: 32711025
  - **机理研究**: GCA偶联聚苯乙烯纳米粒 → ASBT内吞 + 乳糜微粒通路, Adv Sci 2022

### 策略3: 胆酸/药物静电复合物 (Bile Acid-Drug Complex)
- 利用胆汁酸的疏水+亲水双重性质，与药物形成非共价复合物
- 疏水离子配对（HIP）增强包封率和载药量
- **代表**: 甘氨脱氧胆酸钠(SGDC) + 胰岛素的HIP复合物, J Control Release 2021

## 三、核心文献速览

| # | 论文 | 年份 | 期刊 | 核心数据 | 对欣肽的价值 |
|:-:|:----|:----|:-----|:---------|:------------|
| 1 | Deoxycholic acid-chitosan NPs for oral insulin | 2017 | Biomaterials | **口服Bioav 15.9%** (大鼠) | ASBT-LNP路线最经典的benchmark |
| 2 | GCA-chitosan coated liposomes for Ex-4 | 2020 | J Control Release | **口服Bioav 19.5%** vs sc | GLP-1类多肽的ASBT递送验证 |
| 3 | GCA-polystyrene NPs: mechanism study | 2022 | Adv Sci | ASBT内吞+乳糜微粒通路 | 双通道运输机理参考 |
| 4 | GCA-chitosan liposomes (PTX/quercetin) | 2024 | Biomater Sci | ER/Golgi通路转运 | 胞内转运路径参考 |
| 5 | Charge-based supramolecular peptide nanocomplexes | 2025 | Biomaterials | 比天然胆酸**更高亲和力**的ASBT结合基团 | 最新方向：超分子设计替代共价偶联 |
| 6 | Harnessing ASBT for oral peptide delivery (review) | 2025 | Expert Opin Drug Deliv | 三种策略综述 | 系统入门最佳起点 |

## 四、N-Tab vs ASBT-PLGA 在欣肽内部的定位

| 维度 | PenDP N-Tab | ASBT-PLGA |
|:----|:------------|:----------|
| **吸收机制** | 蛋白冠 → 受体介导内吞 → 内体逃逸（积雪草酸膜融合） | 胆酸配体 → ASBT介导内吞 → 细胞内转运 |
| **载体材料** | AA+ELP+LNP（四组分脂质体） | PLGA纳米粒 + 表面胆酸修饰 |
| **递送原理** | 纳米颗粒整体被吸收 | 胆酸配体"搭便车"通过ASBT进入细胞 |
| **Bioav潜力** | 中等（预期<20%，需实验验证） | 中等（文献benchmark 15-20%） |
| **优势** | 靶向性可调（多肽修饰多样化）、内体逃逸机制内置 | PLGA是FDA批准材料、生产工艺成熟、文献支撑充分 |
| **风险** | LNP的寡核苷酸/疫苗经验多，但口服LNP尚未有上市产品 | 口服PLGA纳米粒主要在动物阶段，CICD问题待解 |
| **与PenDP的协同** | 核心管线 — Eleven维评分+Gate Pipeline完善 | 可作为平行探索，共用湿实验平台 |

## 五、搜索词备忘

需要更新文献时使用以下搜索词（Brave Search优先）:
- `ASBT PLGA oral peptide delivery` — PLGA+ASBT组合
- `bile acid conjugated nanoparticle oral bioavailability` — 胆酸修饰纳米粒的in vivo数据
- `deoxycholic acid chitosan insulin oral` — 经典15.9% bioav那篇
- `ASBT prodrug oral peptide` — 前药偶联路线
- `GCA conjugated liposome oral` — 甘氨胆酸修饰脂质体
- `site:cnki.net 胆汁酸偶联 口服多肽` — 中国团队相关研究
