# PENdp V3 Gate Design — PeptAI-inspired

## 设计哲学

从 PeptAI 的 8+1 验证门体系学习，将 PENdp 的 V2「并行评分 → 加权总分」升级为 V3「8维评分 → 8门串行筛选 → Gate判定 + 加权总分」。

### 核心理念
- **串行门控 > 并行评分**: 致命缺陷不应被高分维度平均掉
- **三态决策**: PASS ✅ / FAIL ❌ / COND ⚠️ 取代二值阈值
- **75%规则**: 关键+重要门通过率 ≥75% 方可推进（PeptAI 模式）
- **CRITICAL gate FAIL → 立即终止**: 不浪费后续计算

## Gate 定义

### G1: 靶向基序验证 🔴 CRITICAL
- 维度: D1 (靶向基序)
- PASS ≥6.0 | FAIL <3.0
- 检查: RGD/NGR/CendR/CD206/EGFR 等已知靶向基序
- FAIL原因: 无可识别靶向基序 → 递送系统无靶向能力

### G2: 物化性质筛选 🔴 CRITICAL
- 维度: D2 (物化性质)
- PASS ≥5.0 | FAIL <3.0
- 检查: MW≤5000 Da, 溶解性, 电荷平衡, 二硫键稳定性
- FAIL原因: MW>5000/极端疏水/电荷失衡 → 不可成药

### G3: 积雪草酸协同评估 🟢 NICE-TO-HAVE
- 维度: D3 (积雪草酸协同)
- PASS ≥5.0 | FAIL <2.0
- 检查: 双亲性螺旋, Arg/Lys含量 → AA-LNP融合增强
- 非关键: 不影响淘汰判定

### G4: 蛋白冠+LNP兼容 🔴 CRITICAL
- 维度: D4 (蛋白冠+LNP兼容)
- PASS ≥5.0 | FAIL <3.0
- 检查: 蛋白冠形成潜力, 双亲性平衡, LNP表面展示
- FAIL原因: LNP兼容性极差 → 递送系统核心功能失效

### G5: 脱靶风险控制 🟡 IMPORTANT
- 维度: D5 (Off-target规避)
- PASS ≥5.0 | FAIL <3.0
- 检查: 序列长度/特异性/多阳离子风险
- FAIL原因: 脱靶风险过高 → 系统性毒性

### G6: 合成可行性 🟡 IMPORTANT
- 维度: D6 (合成可行性)
- PASS ≥5.0 | FAIL <3.0
- 检查: 长度/疏水段/聚集倾向
- FAIL原因: 合成难度过高 → 产率/纯度不可控

### G7: ESM相似度参考 🟢 NICE-TO-HAVE
- 维度: D7 (ESM相似度)
- PASS ≥5.0 | FAIL <1.0
- 仅信息: 序列空间远离已知功能肽时标记

### G8: 偶联方向定向性 🟢 NICE-TO-HAVE
- 维度: D9 (偶联定向性)
- PASS ≥5.0 | FAIL <2.0
- 检查: Cys末端放置, 内部Lys数 → LNP定向偶联
- COND常见: 内部Lys≥2时方向性下降

## 三态决策详解

| 状态 | 含义 | 对CRITICAL gate | 对IMPORTANT gate | 对NICE gate |
|:-----|:-----|:---------------|:----------------|:-----------|
| **PASS** | 通过 | 正常 | 正常 | 正常 |
| **FAIL** | 失败 | ⛔ 立即淘汰 | ⚠️ 贡献到75%计数 | 仅标记 |
| **COND** | 条件通过 | — | 允许继续但标记风险 | 允许继续 |

## 与 V2 的对比

| | V2 | V3 |
|:--|:---|:---|
| 失败模式 | 总分<50 → not_recommend | G1/G2/G4 FAIL → 立即淘汰 |
| 风险标记 | 无 | COND (G3/G5/G6/G8) |
| D9 | 未接入 (score=0) | 正式接入 5%权重 |
| 权重 | 8D, Σ=1.0 | 8D, Σ=1.0 (重平衡) |
| 可推进判定 | total≥65 | total≥65 + gate通过率≥75% |

## 参考

- PeptAI 8+1 Gate: G0(校准) → G1(结构) → ... → G9(湿实验)
- 对标分析: `references/peptai-benchmark.md`
- 代码: `pendp/scoring/gates.py`
