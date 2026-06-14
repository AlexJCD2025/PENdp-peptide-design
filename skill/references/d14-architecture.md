# D14 评分架构决策记录 (2026-05-27)

## 激活状态
- **当前**: D14_WEIGHT=0.05 (已激活)
- **关闭**: D14_WEIGHT=0.0
- **单源**: config.py 第24行，所有模块从此导入

## 评分公式
```
D14 = pLDDT(0-3分) + MD_RMSD(0-4分) + QSAR_ADMET(0-3分) = 0-10分

pLDDT多级:
  >70 → +3.0 (高置信,良好折叠)
  >50 → +1.5 (中置信,部分有序)
  >30 → +0.5 (低置信,短肽典型范围)
  ≤30 → +0.0 (基本无序)

MD:
  RMSD < 2Å → +4.0 (动态稳定)

QSAR:
  ADMET三级过滤全通过 → +3.0
```

## 管线阶段
```
orchestrator.run_full_pipeline():
  Stage 1: ML广筛 + 评分引擎 → 全量候选
  Stage 2: ESMFold粗筛(skip_md=True) → Top 50
  Stage 3: 全管线(MD启用) → Top 20
  Stage 4: D14终排 → Top 5-10
  Stage 5: 湿实验标签
```

## 权重调整
- `update_weights_with_d14()`: 动态调整——高D14分增强结构维度,低分增强序列维度
- `patch_engine_weights()`: 保留但标记deprecated, 转发到前者
- 权重总和始终=1.0 (自动重归一化)

## 激活验证
- 回归测试: `tests/test_d14_regression.py` — 5条肽段×多维度 = 89项检查
- 激活前(weight=0.0): D14不贡献
- 激活后(weight=0.05): D14贡献~2-4分调整,权重总和1.0

## 修复历史
1. IPA补丁 → pLDDT 46→60
2. 多元阈值 → 短肽也有区分度
3. QSAR真实实现(RDKit) → 三级过滤+pIC50
4. MD真实实现(OpenMM) → 440行管线
5. 权重单源 → config.py统一
6. 管线合并 → orchestrator+integration统一
