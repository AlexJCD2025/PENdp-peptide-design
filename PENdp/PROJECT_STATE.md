# PENdp Project State
**最后更新:** 2026-05-13
**版本:** v1.0 融合版
**Git:** `git log` 查看提交历史

## 代码是唯一真相来源

> ⚠️ **重要**：此项目的一切领域知识（评分、决策、竞争、湿实验、文献），已全部移植为 `pendp/` 下的 Python 代码模块。**不要从 Skill 文档中抄录任何评分/决策数据**——代码已过期或有更新，以 `pendp/` 包为准。

## 项目位置

```
代码: ~/.hermes/workspace/PENdp/pendp/
安装: pip install -e ~/.hermes/workspace/PENdp
入口: pendp (CLI命令) 或 from pendp import ... (Python API)
```

## 模块职责总览

| 模块 | 位置 | 状态 | 说明 |
|:-----|:-----|:------|:------|
| **评分引擎** | `pendp/scoring/engine.py` | ✅ 核心 | 7D v2.0 + D9偶联 + curated双轨 |
| **数据库** | `pendp/database/` | ✅ 稳定 | 肺靶向v6(13条) + 靶点图谱(15受体) |
| **ESM-2** | `pendp/esm/` | ✅ 可用 | 惰性加载8M/35M/150M/650M |
| **CPP** | `pendp/cpp/classifier.py` | ✅ 可用 | ML+规则fallback |
| **决策** | `pendp/decision/framework.py` | 🆕 融合 | 五大子系统 + 管线 + 对赌 |
| **竞争** | `pendp/decision/competition.py` | 🆕 融合 | 7竞品对标 |
| **湿实验** | `pendp/wetlab/tracker.py` | 🆕 融合 | 7任务追踪 |
| **文献** | `pendp/literature/papers.py` | 🆕 融合 | 7篇论文 + 全文txt (6/7篇已获取) |
| **语义搜索** | `pendp/search/engine.py` | 🆕 v1.0 | jina-v5-omni MLX本地; 文献全文索引(0.2s/20条); 相似度从~0.1→0.5+ |
| **管线** | `pendp/pipeline/orchestrator.py` | ✅ 稳定 | 五关漏斗 + Stage 0 |

## 待接入模块（stub）

| 阶段 | 工具 | 状态 |
|:-----|:------|:------|
| 第二关 | AlphaFold3 / HADDOCK | ⏳ stub — 按评分取Top 50 |
| 第三关 | GROMACS / OpenMM | ⏳ stub — 按评分取Top 20 |
| 第四关 | RDKit + XGBoost / GNN | ⏳ stub — 按评分取Top 5-10 |

## v2.1 待优化方向

1. D3 积雪草酸协同 5% → 8-10%（权重调整）
2. 增加 D9 偶联方向定向性到正式评分体系（当前为实验性）
3. ESM-2 模型下载后首次加载验证
4. 湿实验数据回流 → ML 模型重训练

## CLI 命令速查

```bash
pendp score --seq CRGDKGPDC              # 规则评分
pendp score curated --seq iRGD            # 参考评分 (88.6)
pendp compare --a CRGDKGPDC --b KPSSPPEE # 两肽对比
pendp db list                             # 数据库
pendp db targets                         # 靶点图谱
pendp cpp --seq CRGDKGPDC                # CPP预测
pendp decision --subsystems               # 靶向子系统
pendp decision --pipeline                 # 管线优先级
pendp decision --evaluate IPF             # 适应症评估
pendp competition                         # 竞争格局
pendp wetlab --timeline                   # 湿实验时间线
pendp literature                          # 文献
pendp pipeline --db                        # 五关漏斗
pendp info                                # 平台信息
```
