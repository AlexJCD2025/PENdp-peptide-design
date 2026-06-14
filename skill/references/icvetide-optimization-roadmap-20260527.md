# PENdp iCVETide® 驱动优化路线图

**创建**: 2026-05-27 | **版本**: v1.0
**来源**: iCVETide® (诺和晟泰 STC009, J. Med. Chem. 2025) 对标分析

## 差距全景

```
iCVETide 已跑通:                              PENdp 当前状态:
分子对接 (Docking) ✅                           AF3 → 🔴 stub
动力学模拟 (MD) ✅                              MD → 🔴 stub
多肽合成 (Auto) ✅                              QSAR → 🔴 stub
生物评价 (In Vivo) ✅                           湿实验 → 🟢 有数据但无标准化流程
方法学论文 (JMC) ✅                             方法学论文 → 🔴 无
PCC → GLP → IND ✅                              PCC → 🟡 在研
```

## P0: 补 AF3/MD/QSAR Stubs（1-2 周）

### 实施计划

```python
pendp/pipeline/
  ├── __init__.py
  ├── orchestrator.py    # 改写：串联 AF3 → MD → QSAR
  ├── af3_runner.py      # [新增] 结构预测
  ├── md_runner.py       # [新增] 分子动力学模拟 (OpenMM)
  └── qsar_runner.py     # [新增] ADMET 预测 (RDKit/DeepChem)
```

| 模块 | 工具 | 工作量 | 集成方式 |
|:----|:-----|:------|:---------|
| AF3 预测 | ColabFold 轻量版 / ESMFold | 2-3 天 | subprocess 调用，解析 PDB → 存入数据库 |
| MD 模拟 | OpenMM（Apple Silicon Metal 加速） | 3-5 天 | 对 AF3 PDB 做 10-50ns MD，提取稳定性指标 |
| QSAR 预测 | RDKit + DeepChem（均已安装） | 1-2 天 | ADMET 预测，D14 评分输入 |

### 评分引擎配套改造

新增 `D14 结构可信度(5%)`，权重从 D2/D4 各借 2.5%：

```
D14 结构可信度 (5%):
  - AF3 pLDDT > 70 → +3 分
  - MD 稳定性 (RMSD < 2Å) → +4 分
  - QSAR ADMET 通过 → +3 分
  - 满分 10 分 × 5% 权重 = 最高 0.5 分
```

## P1: 标准化计算→湿实验闭环（1 周）

### Feedback Loop 设计

```python
class WetlabFeedbackLoop:
    """iCVETide 风格的多级筛选迭代"""
    def register_result(self, seq_id, assay_data):
        """注册湿实验结果，计算预测 vs 实际偏差"""
    def recalibrate(self, seq_ids):
        """基于 N 个数据点重新校准 D1-D13 权重"""
        # 使用已安装的 pymoo 做多目标优化
        # 目标：最小化 预测分 vs 实验活性 的 RMSE
```

### 与 iCVETide 对标

| iCVETide 步骤 | PENdp 实现 |
|:--------------|:-----------|
| In Silico 初筛 | 12 维评分 ✅ |
| 分子对接精筛 | AF3 结构预测 🆕 |
| MD 验证 | OpenMM 动力学 🆕 |
| 合成 | 手动合成 |
| 生物评价 | 湿实验跟踪 ✅ |
| 反馈到计算 | Feedback Loop 🆕 |

## P1: 方法学论文（4-8 周）

**目标期刊**: Journal of Medicinal Chemistry 或 European J. Med. Chem.

**已有数据**:
- ✅ 12 维评分 + 条件激活 D13
- ✅ 12 门门控 G1-G12
- ✅ ESM-2 语义搜索
- ✅ AA-LNP/ELP-LNP 湿实验数据
- ✅ 脑靶向序列库

**需补实验**:
- 1-2 条序列从评分→AF3→MD→合成→活性测试（端到端验证）
- 与已知多肽的基准测试对比（1 周纯计算）

## 优先级路线图

```
Week 1-2: P0 — AF3/MD/QSAR Stubs
  ├── 安装 ColabFold/OpenMM/DeepChem
  ├── af3_runner.py → pLDDT 评分
  ├── md_runner.py → MD 稳定性评分
  ├── qsar_runner.py → ADMET 预测
  └── D14 结构可信度并入评分引擎

Week 3-4: P1 — 计算→湿实验闭环
  ├── feedback_loop.py
  ├── 用已有 AA-LNP/ELP-LNP 数据校准
  └── 校准报告

Week 4-8: P1 — 方法学论文
  ├── 端到端案例
  ├── manuscript
  └── 目标 JMC/EJMC
```
