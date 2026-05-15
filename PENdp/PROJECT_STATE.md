# PENdp Project State
**最后更新:** 2026-05-15
**版本:** v4.0 — PeptAI Full Integration
**Git:** `git log` 查看提交历史

## V4 更新摘要 (2026-05-15)

PeptAI 七项经验全面落地：

| # | 功能 | 来源 | 模块 |
|:--|:-----|:-----|:-----|
| 🎯 | G0 校准门 | PeptAI G0 Calibration | `gates.py::calibrate()` |
| 📋 | Gate JSON 审计日志 | PeptAI On-chain Log | `gates.py` log_json |
| 💡 | COND 智能建议 | PeptAI Agent Decision | `GateDef.cond_suggestion` |
| 🔬 | 结构分析（Chou-Fasman+ESM） | PeptAI G1 Structure | `structure.py` 🆕 |
| 📊 | 批量 Gate 感知排序 | PeptAI Fleet Ranking | `gates.py::evaluate_batch()` |
| 🧬 | 虚拟定向进化 | PeptAI Generation Iteration | `evolution.py` 🆕 |
| 🏷️ | 权重重平衡 + D9 正式接入 | V3 | `config.py` |

## V4 新增 CLI

```bash
pendp score --seq X --gates --calibrate      # 🎯 G0 校准参考肽基线
pendp score --seq X --gates --log-json       # 📋 Gate 决策 JSONL 审计日志
pendp score --seq X --gates --log-json       # (输出可 pip 到文件做 audit trail)
pendp score --seq X --structure              # 🔬 结构特征分析
pendp score --seq X --evolve --rounds 3      # 🧬 定向进化 (3轮)
pendp score --file seqs.txt --gates --rank   # 📊 批量 Gate 感知排名
```

## 模块职责总览

| 模块 | 位置 | 状态 | 说明 |
|:-----|:-----|:------|:------|
| **评分引擎** | `pendp/scoring/engine.py` | ✅ V4 | 8D + Gate Pipeline + batch_gate_score |
| **门控引擎** | `pendp/scoring/gates.py` | ✅ V4 | G0校准 + 8门 + COND建议 + JSON日志 + Gate排序 |
| **结构分析** | `pendp/scoring/structure.py` | 🆕 V4 | Chou-Fasman + ESM-2 结构特征 |
| **定向进化** | `pendp/scoring/evolution.py` | 🆕 V4 | 虚拟定向进化 (单点突变→Gate筛选→多轮) |
| **数据库** | `pendp/database/` | ✅ 稳定 | 肺靶向v6(13条) + 靶点图谱(15受体) |
| **ESM-2** | `pendp/esm/` | ✅ 可用 | 惰性加载8M/35M/150M/650M |
| **CPP** | `pendp/cpp/classifier.py` | ✅ 可用 | ML+规则fallback |
| **决策** | `pendp/decision/framework.py` | ✅ | 五大子系统 + 管线 + 对赌 |
| **竞争** | `pendp/decision/competition.py` | ✅ | 7竞品对标 |
| **湿实验** | `pendp/wetlab/tracker.py` | ✅ | 7任务追踪 |
| **文献** | `pendp/literature/papers.py` | ✅ | 7篇论文 + 全文txt |
| **语义搜索** | `pendp/search/engine.py` | ✅ | jina-v5-omni MLX本地 |
| **管线** | `pendp/pipeline/orchestrator.py` | ✅ | 五关漏斗 + Stage 0 |

## V4 Gate Pipeline

```
G0 ─ 🎯 校准: 参考肽(iRGD/iNGR/KP-10/RP-832c/CREKA/A6) → 设定基线
G1 ─ [!!] 靶向基序 → CRITICAL FAIL → 立即淘汰
G2 ─ [!!] 物化性质 → CRITICAL FAIL → 立即淘汰
G3 ─ [  ] 积雪草酸协同 → NICE, COND + 💡建议
G4 ─ [!!] LNP兼容 → CRITICAL FAIL → 立即淘汰
G5 ─ [! ] 脱靶风险 → IMPORTANT, COND + 💡建议
G6 ─ [! ] 合成可行性 → IMPORTANT, COND + 💡建议
G7 ─ [  ] ESM相似度 → NICE, COND + 💡建议
G8 ─ [  ] 偶联定向 → NICE, COND + 💡建议
```

每道门输出 JSON 审计记录:
```json
{"ts": "2026-05-15T15:20:48Z", "seq": "CRGDKGPDC", "gate": "G1", "status": "PASS", "score": 9.5, "pass_threshold": 6.0}
```

## G0 校准基线 (参考肽)

| 维度 | Mean | Stdev | P25 | P75 |
|:-----|:-----|:------|:----|:----|
| D1 靶向基序 | 7.2 | 1.6 | 6.2 | 8.0 |
| D2 物化性质 | 7.4 | 0.7 | 7.1 | 7.5 |
| D3 积雪草酸协同 | 6.0 | 0.9 | 5.2 | 6.8 |
| D4 蛋白冠+LNP | 6.4 | 1.4 | 5.4 | 7.4 |
| D5 脱靶风险 | 7.0 | 1.1 | 6.2 | 7.8 |
| D6 合成可行性 | 8.3 | 0.9 | 7.8 | 8.9 |
| D7 ESM相似度 | 5.0 | 0.0 | 5.0 | 5.0 |
| D9 偶联定向性 | 6.6 | 2.2 | 5.0 | 8.2 |

## V3→V4 能力跃迁

| 能力 | V3 | V4 |
|:-----|:---|:---|
| Gate决策 | PASS/FAIL/COND | + G0校准 + 💡COND建议 + JSON审计 |
| 结构信息 | 无 | Chou-Fasman + ESM-2 特征 |
| 批量处理 | 逐个评分 | Gate感知排名 |
| 优化能力 | 手动设计 | 虚拟定向进化自动探索 |
| 可审计性 | print only | JSONL完整决策链 |
