# 脑靶向LNP序列分析报告 (2026-05-26)

## 背景
从13条LNP多肽修饰序列库中筛选脑靶向候选，经7维脑靶向定制评分框架深度打分。

## 核心结论
- **首选**: T7 (CHAIYPRH, TfR1) — 82.8分, 最佳平衡: BBB穿透+合成成本最低+与PENdp兼容
- **并列首选**: RVG29 (29aa, nAChR) — 80.8分, CNS神经元特异性最高
- **组合方案**: T7+HA2共修饰 (靶向+内体逃逸双功能)
- **配方增益**: AA作为五组分添加(20%替代CHOL, 借鉴北大UA策略)

## 架构决策: D13条件注册
D13不能直接以8%加入通用评分(非脑靶向肽被压低2-5分)。
采用**条件注册+模式切换**: D13默认weight=0, `--mode brain`时激活。

## 参考文件
- `/tmp/brain-targeting-sequence-analysis.md` — 完整7维评分报告(378行)
- `/tmp/brain-dimension-architecture-decision.md` — ADR架构决策记录(283行)
- `references/lnp-peptide-library-20260526.md` — Excel 13条序列库参考
