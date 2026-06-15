# 口服生物药递送技术路线 — 全景分析

> 2026-05-22 更新 v2 | 新增ASBT/胆汁酸通路第三路线

## 三类口服生物药递送技术路线

| 类别 | 技术 | 核心逻辑 | 代表 | 阶段 |
|:-----|:-----|:---------|:-----|:-----|
| **机械物理** | 可溶针机器人胶囊/肠溶包衣 | **绕过**吸收屏障（物理穿刺/注射） | RaniPill(Rani Therapeutics), Entera(EB613) | I期-III期 |
| **化学纳米** | ELP-LNP+多肽修饰 | **穿过**吸收屏障（受体介导内吞） | PenDP N-Tab (欣肽生物) | DLS表征 |
| **胆汁酸通路** | 胆酸偶联PLGA纳米粒 | **搭便车**内源性转运体（ASBT介导内吞） | 欣肽生物 ASBT-PLGA | 项目调研阶段 |

---

## 一、Rani Therapeutics 全景 — 机械物理路线案例

### 公司概况
- **上市代码**: RANI (Nasdaq)
- **市值**: ~$75-105M（微盘股）
- **股价**: ~$0.93-1.09（**低于$1退市红线**，180天补救期至2026-11-09）
- **现金**: $43.4M（2026Q1末），跑道至2027Q4
- **CEO**: Talat Imran

### 技术 — RaniPill 机器人胶囊

**机制**: 
```
吞咽 → 肠溶包衣(耐胃酸) → 小肠(pH升高,包衣溶解)
→ 两种化学物质反应生成CO₂ → 气球膨胀 
→ 推出可溶性聚合物针 → 针刺入肠壁
→ 药物释放入血 → 针溶化+气球泄气 → 排出
```

核心洞察: **肠道没有痛觉神经**，所以针刺是痛感的。药物物理绕过所有胃肠道吸收屏障。

### 管线

| 编号 | 适应症 | 药物类型 | 进度 | 状态 |
|:----|:-------|:---------|:-----|:-----|
| RT-102 | 骨质疏松 | PTH(1-34) | **I期完成** | ⏸️ 搁置（资源转向GLP-1） |
| RT-114 | 肥胖 | GLP-1/GLP-2双激动剂 | **I期进行中(2026年1月启动)** | 🟢 优先管线 |
| RT-105 | 自身免疫 | TNFα抗体 | 临床前 | ⏸️ |
| RT-111 | 炎症 | 乌司奴单抗生物类似药 | 临床前 | ⏸️ |
| 合作管线 | 罕见病/免疫 | Chugai抗体 | 合作开发 | 🟢 |

### 财务状况 — 生死转型

```
2023 H2: 宣称RT-102 II期即将启动（但从未发生）
2024:    无进展，现金持续消耗
2025 Q3: 仅剩 $4.1M（≈3个月跑道）⚠️ 接近死亡
2025-10: Chugai合作（$10M upfront, 潜在$1.085B）+ $60.3M PIPE融资
         现金从$4.1M → $49.7M ✅
         管理层明确: "聚焦最大临床和商业潜力的项目" = GLP-1
2026-01: RT-114 (GLP-1/GLP-2) I期启动
2026-05: 现金$43.4M，股价~$1以下面临退市
```

### RT-102 数据亮点
- **Bioav**: 口服PTH比注射Forteo高 **300-400%**
- **递送成功率**: 90%+ 胶囊成功释放药物
- FDA同意走 **505(b)(2)** 路径
- 但市场够小（骨质疏松），资本够缺，最终搁置

### RT-114 (GLP-1) 数据
- 临床前: **bioequivalence** 与皮下注射（相当于注射，不是超越）
- 已证明口服Semaglutide可行（临床前）
- 对比: RT-102的300-400% > RT-114的bioequivalence
- 但市场大小: GLP-1 >> 骨质疏松

### 合作: Chugai (中外制药, 日本)
- 首付: $10M
- 里程碑: 技术转让+开发里程碑 up to $75M
- 销售里程碑: up to $100M + 个位数特许权使用费
- 可扩展至最多5个额外靶点（潜在总价值$1.085B）

---

## 二、三类技术路线对比矩阵

| 维度 | 机械物理 | 化学纳米 (PenDP N-Tab) | 胆汁酸通路 (ASBT-PLGA) |
|:----|:---------|:----------------------|:----------------------|
| **Bioavailability** | 高（可接近注射，RT-102达300-400%） | 低-中（典型口服LNP 1-20%） | 中（文献benchmark 15-20%） |
| **药物通用性** | 极强 — 任何大分子药都能搭载 | 中等 — 需适配LNP包封条件 | 中等 — 需胆酸偶联能力 |
| **临床验证深度** | I期完成（Rani RT-102, 90%+递送成功率） | DLS表征阶段（~80-95nm, PDI~0.26） | 主要在动物阶段，无人临床 |
| **器械复杂度** | 高 — 可溶针+化学反应+气球+pH触发 | 中 — 微流控合成+冻干 | 中 — PLGA纳米粒制备（成熟工艺） |
| **长期安全性** | 未知 — 反复针刺肠段累积效应 | 高 — LNP亿级剂mRNA疫苗数据背书 | 中高 — PLGA是FDA批准材料但口服PLGA数据有限 |
| **监管路径** | 组合产品（drug-device），审批更复杂 | 单一NDA（505(b)(2)），更简洁 | 单一NDA（505(b)(2)），PLGA有先例 |
| **规模成本** | 高（精密胶囊组装，>$5/粒） | 低（微流控合成，<$1/剂） | 中（PLGA纳米粒生产中） |
| **患者体验** | 吞咽大胶囊（~2cm，可能有异物感） | 正常口服 | 正常口服 |

---

## 三、对PenDP的关键启示

1. **Bioav不是唯一战场** — RaniPill在bioav上完胜，但这不妨碍他们因市场太小而放弃骨质疏松。市场大小 > 技术指标
2. **安全性+成本+靶向是差异化路径** — LNP在这些维度有结构性优势
3. **Rani的GLP-1转舵验证了GLP-1赛道拥挤度** — 即使手握300-400% bioav的独特技术，也要追GLP-1
4. **现金跑道决定管线** — Rani的教训: 好数据+好技术 ≠ 能活下来。PenDP应关注差异化适应症（脑靶向/肺靶向）和务实开发路径
5. **欣肽内部ASBT-PLGA与N-Tab是平行探索** — 两者机制、材料、路径均不同。ASBT路线的benchmark（15-20% bioav）可作为技术目标参考，但不直接比较

---

## 四、参考文献

- Rani Therapeutics IR: https://ir.ranitherapeutics.com/
- RaniPill Technology: https://www.ranitherapeutics.com/technology/
- Chugai合作公告 (2025-10): https://www.globenewswire.com/news-release/2025/10/17/3168550/0/en/
- RT-102 Phase 1数据: https://ir.ranitherapeutics.com/news-releases/news-release-details/rani-therapeutics-announces-positive-topline-results-phase-1/
- RT-114 Phase 1启动 (2026-01): https://ir.ranitherapeutics.com/news-releases/news-release-details/rani-therapeutics-initiates-phase-1-study-rt-114-ranipillr/
- 2026Q1财报: https://ir.ranitherapeutics.com/news-releases/news-release-details/rani-therapeutics-reports-first-quarter-2026-financial-results
- ASBT口服递送文献综述: `references/asbt-bile-acid-oral-delivery.md`
