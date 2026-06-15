# K-Dense Scientific Skills 集成 (PENdp V4.1)

## 来源
- 仓库: K-Dense-AI/scientific-agent-skills (21.8k stars, MIT)
- 安装日期: 2026-05-16
- 已装至 PENdp: deepchem, rdkit, datamol, pytdc, medchem, diffdock, glycoengineering, esm (8个)

## 已集成维度

### D10: ADMET/药化过滤 (7%)
- 来源: K-Dense medchem skill
- 实现: `score_medchem_filter()` in engine.py
- 规则: Lipinski适配(多肽版), PAINS模式(CC/WW/FF/CCCC), 结构警报(Cys/Poly-Arg)
- 门控: G9 (IMPORTANT)

### D11: 糖基化影响 (5%)
- 来源: K-Dense glycoengineering skill
- 实现: `score_glycoengineering()` in engine.py
- 规则: N-glyco sequon(N-X-S/T), O-glyco热点(S/T比例), Pro阻断
- 门控: G10 (NICE)

## 权重重平衡

| Dim | V4 | V4.1 |
|-----|----|------|
| D1  | 25% | 22% |
| D2  | 18% | 13% |
| D10 | -   | 7%  |
| D11 | -   | 5%  |

## 审查记录
- 2026-05-16: D2/D10重复惩罚 → 已修; Cys检测过断言 → 加注释
