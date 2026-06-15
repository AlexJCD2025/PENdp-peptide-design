# PENdp 科学化路线图 — 从"规则计算器"到"可验证的预测模型"

状态: 草案 v1 · 2026-06-15 · 适用分支 `claude/ai-multimodal-code-review-f820ha`

---

## 0. 核心判断（为什么需要这份路线图）

PENdp 当前的评分（`pendp/scoring/engine.py` 的 D1–D9 + D14）**全部是手写阈值**，权重在
`pendp/config.py::SCORING_DIMENSIONS` 里手工设定，所谓"校准"只用了
`pendp/scoring/gates.py::REFERENCE_PEPTIDES` 里的 **6 条参考肽**（统计上无意义）。

> 关键事实：**整个代码库里没有任何一个数字能回答"这套评分到底预测得准不准"。**

ESMFold / AF3 / MD / QSAR（`pendp/pipeline/integration.py`、`af3_runner.py`）目前是
**基于序列特征的启发式 proxy**，不是真实模型。

因此本路线图只有一条主线：**建立验证 → 用数据替换手拍权重 → 持续按验证指标演进**。
其余都是支线。

---

## 1. 北极星指标（Definition of Done 的锚点）

所有评分相关改动，最终都用一个指标衡量：

> **留出集上，PENdp 总分（及各维度分）与真实湿实验读数之间的等级相关性（Spearman ρ）。**

- 没有这个数字之前，任何"评分更好了"的说法都不成立。
- 验收门槛（建议起步值，可随数据调整）：
  - **及格**：留出集 Spearman ρ ≥ 0.4（显著优于随机，且优于"只看长度/电荷"的朴素基线）。
  - **可用**：ρ ≥ 0.6，且学习模型在留出集上**稳定优于**手拍启发式基线。
- 同时报告：每个维度单独 vs 读数的相关性（哪些维度真有预测力，哪些是噪声/冗余）。

---

## 2. 分阶段计划

### Phase 0 — 让现状"可被测量"（现在就能做，不依赖大量数据）

**目的**：先有体温计，再谈治病。即使只有 20–50 条带读数的肽，也能算出基线相关性。

**交付**
- 数据 schema（最小可用）：新增 `pendp/data/wetlab_results.csv` + 加载器，列定义：
  ```
  sequence, target, assay, readout, value, unit, direction, n_replicates, batch_id, date, source, notes
  # direction: "higher_better" | "lower_better"（统一相关性方向）
  ```
- 评估模块 `pendp/eval/__init__.py`：
  ```python
  def evaluate_scoring(dataset, scorer) -> EvalReport:
      """对每条肽算 scorer 分，与 value 求 Spearman/Pearson。
      返回 {n, spearman, pearson, per_dimension_corr, baseline_corr}。"""
  ```
- CLI：`pendp eval --dataset wetlab_results.csv`（打印总分相关性 + 每维度相关性 + 朴素基线对照）。
- 朴素基线（必须有，作为下限参照）：仅用"长度 + 净电荷 + 疏水比"线性拟合的相关性。

**退出标准**：能对任意带标签数据集一键产出 Spearman ρ 报告；当前手拍评分的基线 ρ 被记录在案。

---

### Phase 1 — 闭合湿实验回路（数据管道）

**目的**：把"第五关 湿实验闭环"从 stub 变成真实数据入口。现有
`pendp/wetlab/tracker.py` 只追踪**任务**，不接收**结果**。

**交付**
- 扩展 tracker：`add_result(...)` 写入 `wetlab_results.csv`（schema 同 Phase 0）。
- CLI：`pendp wetlab add-result --seq ... --assay binding --value ... --unit nM --direction lower_better`。
- 数据卫生：去重、单位归一化、同一肽多批次取均值/记录方差、异常值标记。
- 最小启动数据集目标：**≥ 30 条**有可比读数的肽（同一 assay/target 优先）。

**退出标准**：湿实验数据能持续、规范地流入仓库，`pendp eval` 直接消费。

---

### Phase 2 — 用学习模型替换手拍权重（数据量达标后）

**前置**：引入一层可替换的打分接口，让"启发式"和"学习模型"对调用方透明：
```python
# pendp/scoring/base.py
class Scorer(Protocol):
    def predict(self, seq: str) -> ScoreResult:  # {score, confidence, per_dimension}
        ...
```
现有 `ScoringEngine` 实现 `Scorer`（启发式版）；学习模型实现同一接口即可热插拔，**不改任何调用方**。

**Phase 2a（小样本，N≈30–100）— 只学权重，保留可解释维度**
- 特征 = 现有 9 个维度分（D1–D9，D14）。
- 模型 = 带正则的线性/逻辑回归 或 learning-to-rank（pairwise）。
- 用嵌套交叉验证报告留出集 Spearman；**正则会自动把冗余维度权重压到 ~0**（顺带完成 Phase 3 的去冗余）。
- 决策门：**学到的权重在留出集上必须打败 Phase 0 的手拍基线**，否则不采用。

**Phase 2b（样本变多）— 放开模型复杂度**
- 在维度特征上用梯度提升；或直接用 **ESM-2 嵌入**做预测（系统已能算嵌入，
  见 `pendp/esm/embeddings.py`，但目前 D7 默认中性 5.0、从未真正用于预测）。
- 仍然：每次都报留出集相关性，**只在打败更简单模型时才升级**。

**配套**
- 用真实数据集替换 6 条肽的 G0 校准（`gates.py::REFERENCE_PEPTIDES`）。
- 输出**不确定性**：`ScoreResult.confidence`（如分位数回归/集成方差），不再用裸点估计冒充精确。

**退出标准**：`pendp score` 默认走学习模型，且其留出集 ρ ≥ 手拍基线；报告随模型一起版本化。

---

### Phase 3 — 维度去冗余与特征审计

**目的**：现在多个维度在测同一件事 → 变相重复加权。
- `score_physiochem`(D2) / `score_corona_lnp`(D4) / `score_off_target`(D5) 都看疏水比例；
- D3 与 D4 都奖励 R/K；
- 文档自己标注过 "D2/D10 重叠风险"。

**交付**
- 维度间相关性矩阵（在肽库上）+ 维度 vs 读数相关性（在标签集上）。
- 高度相关的维度合并/删除；最终由 Phase 2 的正则化模型给出客观权重。

**退出标准**：维度集精简到"每个维度都有独立、可解释的预测贡献"。

> 注：Phase 3 与 Phase 2a 高度耦合，建议合并推进（正则化天然完成去冗余）。

---

### Phase 4 — 让结构管线变"真"（重、可选、依赖环境）

**目的**：把 proxy 换成真实模型，验证真实结构指标是否比 proxy 更有预测力。
- 接口已就位（`integration.py`/`af3_runner.py` 桩位清晰），按 `setup.py` 的
  `extras_require`（`esm` / `struct`）接：ESMFold（`esm`）、MD（OpenMM）、QSAR（RDKit）。
- **验收同样靠相关性**：真实 pLDDT / MD-RMSD / QSAR 必须在留出集上比 proxy 更准才保留。
- 现实约束：需要 GPU + ~6GB 权重；建议在能跑 GPU 的环境单开分支/PR，不阻塞 Phase 0–3。

---

## 3. 贯穿原则：验证优先（Validation-First）

- **每一个评分改动**都必须报告它对留出集相关性的影响。**严禁**再出现"为了让分数通过而放宽测试"
  （V4.4 曾把 RP-832c 断言从 `<85` 放宽到 `<95` 来掩盖权重虚高 bug）。
- `pendp eval` 进 CI：评分逻辑改动若让相关性显著下降，CI 应提示。
- 模型、权重、数据集都要版本化，结果可复现。

---

## 4. 最小启动路径（建议下一步就做）

1. **现在**：Phase 0 的评估骨架（schema + `pendp/eval` + `pendp eval` CLI + 朴素基线）。
   即使手上只有个位数的真实读数，也先把管道和"体温计"立起来。
2. 同步收集/录入 ≥30 条带读数的肽（Phase 1）。
3. 数据够了就上 Phase 2a（学权重）+ Phase 3（去冗余），用相关性决定取舍。
4. Phase 4 视资源单独排期。

---

## 5. 风险与对策

| 风险 | 说明 | 对策 |
|:-----|:-----|:-----|
| 数据太少 | N<30 时模型不可靠 | 先做 Phase 0/朴素基线；用强正则 + 嵌套 CV；诚实报告置信区间 |
| 实验噪声 | 不同批次/assay 不可比 | schema 强制记录 assay/target/batch/方向；同条件内比较；记录重复方差 |
| 过拟合 | 维度多、样本少 | 正则化 + 留出集 + "必须打败更简单模型"决策门 |
| 指标造假 | 调参迎合测试 | 验证优先原则 + `pendp eval` 进 CI + 留出集不参与训练 |
| proxy 当真 | 把启发式 proxy 误当模型输出 | 文档与字段命名标注 proxy；Phase 4 用相关性证明真实模型更优才替换 |

---

*本路线图只规划方向与接口，不含实现。落地任一 Phase 前应先确认数据可用性。*
