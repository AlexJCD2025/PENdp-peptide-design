# LNP多肽修饰代表性序列库 — 外部参考 (2026-05-26)

来源: 达哥分享的Excel (两份文件完全一致)
定位: LNP表面DSPE-PEG-肽修饰领域的代表性已发表序列
覆盖: 细胞穿透/器官靶向/内体逃逸/免疫逃逸四大功能

## 完整序列列表

| # | 名称 | 序列 | 功能 | 修饰方式 |
|---|------|------|------|---------|
| 1 | TAT (HIV-1) | YGRKKRRQRRR | 细胞穿透肽,促进膜融合 | Tat-PEG脂质 |
| 2 | TAT-DSPE-PEG2K | GRKKRRQRRRPPQC | 脑组织mRNA转染 | DSPE-PEG2K-peptide |
| 3 | RVG29 | YTIWMPENPRPGTPCDIFTNSRGKRASNGC | 神经元转染 | DSPE-PEG2K-peptide SM102 |
| 4 | T7 | CHAIYPRH | 脑部优先递送 | DSPE-PEG2K-peptide SM102 |
| 5 | MH42 | SPALHFLGGGSC | 视网膜mRNA递送 | DSPE-PEG2K-peptide MC3 |
| 6 | HA2 | GLFGAIAGFIENGWEGMIDG | 内体逃逸 | 与mRNA共包封于LNP |
| 7 | C18-肽 | PLRQFLWRKRRLYQTLY-GSG-K(C18) | mRNA递送 | C18脂质偶联 |
| 8 | 3R-LNP | RRR | 肝靶向 | DSPE-PEG-peptide |
| 9 | 6R-LNP | RRRRRR | 肺靶向 | DSPE-PEG-peptide |
| 10 | 6D-LNP | DDDDDD | 脾靶向 | DSPE-PEG-peptide |
| 11 | CD47肽 | GNYTCEVTELSREGKTVIELK | 免疫逃逸(别吃我) | DSPE-PEG-peptide |
| 12 | A5G33 | ASKAIQVFLLAG | 角质形成细胞靶向 | DSPE-PEG2K-peptide |
| 13 | GALA | WEAALAEALAEALAEHLAEALAEALEALAA | Chol-GALA肺靶向 | Chol修饰 |

## 与PENdp现有序列库的对比

无直接序列重叠 — 全部为新序列。
PENdp核心序列(iRGD/iNGR/AKPC/RP-832c等)聚焦肺靶向和肿瘤血管，
Excel序列跨器官(肝/肺/脾/脑/眼/皮肤/视网膜)和功能(逃逸/穿透/免疫)更广。

## 对PENdp的参考价值

### 高价值
1. **HA2 (GLFGAIAGFIENGWEGMIDG)** — pH触发内体逃逸肽
   - 与PENdp AA策略互补：AA依赖膜融合增强, HA2提供独立的pH响应逃逸
   - 建议: 作为D3(AA协同)维度的正面参考, 或G门控的内体逃逸检查项

2. **C18-肽 (PLRQFLWRKRRLYQTLY-GSG-K-C18)**
   - 含C18脂质尾巴的多肽, 无需额外PEG脂质即可锚定LNP
   - 对PENdp: K(C18)修饰策略可替代DSPE-PEG-肽

### 中等价值
3. **电荷-器官靶向规律**: 3R→肝, 6R→肺, 6D→脾
   - 简单有效, 可作为PENdp ELP-LNP表面电荷调控的对照设计
   - 6R→肺靶向与PENdp肺靶向管线直接对标

4. **CD47肽** — 免疫逃逸
   - "别吃我"信号减少MPS清除, 延长LNP循环时间
   - 可考虑作为ELP-LNP的额外表面修饰层

### 参考价值
- TAT: 经典CPP, 可作为阳性对照
- RVG29/T7: CNS靶向, 填补PENdp脑靶向文献缺口
- GALA: pH响应融合肽, Chol修饰策略参考

## 保存

原始Excel文件: 
- ~/.hermes/cache/documents/doc_630f63877f4b_10e99e5946b9cf02.xlsx
- ~/.hermes/cache/documents/doc_0f3955b8e3d9_33cf33f2b0feb46c.xlsx
