# PeptAI 对标分析 — 2026-05-15

> 来源: peptai.xyz / app.bio.xyz / molecule.xyz / Bankless / Delphi Digital
> 用途: PENdp 验证体系升级参考

## PeptAI 概览

BIO Protocol 旗下的自治 AI 多肽药物发现 Agent。Head Agent 协调 4+ 子 Agent 舰队，每个针对单一 GPCR 受体，走 8+1 道验证门，湿实验由 Adaptyv Bio 执行（x402 机器对机器支付），结果上链（Molecule Labs）。

**当前管线**: GLP-1R (Agent-01) / KISS1R (Agent-02) / OX2R (Agent-03) / 社区票选 (Agent-04)
**OX2R-004**: 18残基 ADHD 激动剂，24h 完成计算验证，湿实验估价 $500-600/候选

## 8+1 Gate 体系（从实时日志还原）

```
G0  ─ 校准 (Calibration)
      ChEMBL 已知结合数据标定 → 设定及格线

G1  ─ 结构预测 (Structure)
      RFdiffusion / AlphaFold → 肽-受体复合物结构

G2  ─ 稳定性 (Stability)  
      LiteFold MD (10-50ns), OpenMM 拓扑验证
      例: "C4-02 G2 FAIL — OpenMM protocol-violation"

G3  ─ 结合界面 (Interface)
      PRODIGY → 界面面积 + 结合概率
      例: "C5-05 G3 PASS: 0.921 / 1669 Å²"

G4  ─ 结合能 (Binding Energy)
      Boltz-2 → ΔG_bind 排名
      例: "C5-05 G4 PASS: -12.9 kcal/mol, rank #2"

G5  ─ 动力学 (Dynamics)
      延长 MD → 骨架 RMSD 稳定性
      例: "C5-05 G5 FAIL: BB RMSD 3.684 Å"

G6  ─ 安全性 (Safety/Viability)
      毒性/免疫原性/稳定性预测

G7  ─ 选择性 (Selectivity)
      脱靶筛选 (NPFFR1/NPFFR2等)
      例: "C1-02 G8: NPFFR1 selectivity fail"

G8  ─ 合成就绪 (Synthesis Readiness)
      可合成性 + ncAA 参数化检查

G9  ─ 湿实验 (Wet-lab)
      Adaptyv Bio: BLI + cAMP + 血浆稳定性
      结果上链 Molecule Labs
```

## 关键设计特征

1. **串行门控而非并行评分**: 候选逐门淘汰，不会出现「总分高但致命缺陷被平均」
2. **三态决策**: PASS / FAIL / COND（条件通过，允许继续但标记风险）
3. **~75% 加权通过率即可**: 不需要每道门都 PASS，关键门（G1/G4/G6）必须过
4. **完整审计链**: 每道门的决策、工具调用、数据全部上链公开

## PENdp vs PeptAI: 能力矩阵

| 能力维度 | PeptAI | PENdp (当前) | 差距 |
|:---------|:-------|:-------------|:-----|
| 结构预测 | G1: AlphaFold/RFdiffusion | ❌ 无 | 关键缺口 |
| 分子动力学 | G2/G5: LiteFold MD/OpenMM | ❌ 无 | 关键缺口 |
| 结合界面 | G3: PRODIGY | ❌ 无 | - |
| 结合能 | G4: Boltz-2 | ❌ 无 | - |
| 安全性 | G6: 毒性/免疫原性预测 | ✅ 生物相容性评分 | 类似 |
| 选择性 | G7: 脱靶筛选 | ⚠️ 不适用 | 递送系统概念不同 |
| 可合成性 | G8: ncAA参数化 | ✅ 合成可行性评分 | 类似 |
| 湿实验 | G9: Adaptyv Bio x402 | ❌ 无 | 长期目标 |
| 评分体系 | 串行门控 (PASS/FAIL/COND) | 并行加权 (8维→总分) | **可立即借鉴** |
| 多靶点 | 4受体并行舰队 | 5子系统并行 | 类似架构 |

## 对 PENdp 的行动建议

| 优先级 | 建议 | 预期收益 | 难度 |
|:-------|:-----|:---------|:-----|
| P0 | 在 8 维评分上加 Gate 决策层 (PASS/FAIL/COND) | 防止「高分但有致命缺陷」 | 低 (改评分输出) |
| P1 | 接入 AlphaFold3 或 Boltz-1 做 ELP 结构预测 | 补齐最关键的缺失能力 | 中 (需 GPU) |
| P2 | 调研国内 CRO 自动化合成 API | 湿实验闭环铺路 | 高 |
| P3 | 评估 PRODIGY/Boltz-2 对多肽-受体结合的适用性 | 增强靶向性评分 | 中 |

## PeptAI 的弱点（PENdp 的机会）

- 受体泛化但深度浅（每个受体仅几条候选肽）
- 依赖公开工具链（无自研模型/评分框架）
- Token 经济驱动的叙事风险（$BIO 从 $0.88 跌 98% 到 $0.018 再反弹）
- 湿实验仅 BLI + 结合（无细胞/动物实验）
- 安全/毒性门（G6）为最薄弱环节——PENdp 的生物相容性维度有优势

## 关键参考来源

- PeptAI 平台: https://peptai.xyz/
- BIO Agent 页面: https://app.bio.xyz/agents/peptai
- Molecule 链上项目: https://molecule.xyz/projects/7079364503028251508578684509521557949079851428906896322195700714166025795915
- Bankless 深度分析: https://www.bankless.com/read/ai-rewrites-the-desci-equation
- Tokenist 市场分析: https://tokenist.com/bio-protocol-surges-desci-ai-drug-discovery/
- 科学基础: RFdiffusion (Nature 2023) / AlphaFold (Nature 2021) / Boltz-2 (bioRxiv 2025)
