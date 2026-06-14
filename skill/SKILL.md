---
name: pendp-peptide-design
description: PENdp AI辅助多肽设计平台 V4.4 — 积雪草酸+ELP-LNP+多肽修饰三层协同。含12+1维评分(D13条件激活脑靶向+D14结构可信度)+12门串行门控、AF3/MD/QSAR管线、肺靶向数据库v6、ESM-2语义搜索、竞争对标、管线决策框架
version: 4.4.0
updated: 2026-05-27
author: Super Joey
category: biopharma-framework
tags: [pendp, peptide-design, LNP, drug-delivery, asiatic-acid, ELP, lung-targeting, safety-first, decision-framework, cognitive-upgrade, K-Dense, ASBT, bile-acid, oral-peptide]
related_skills: [biopharma-framework, mlx-local-models-apple-silicon, web-intelligence-radar, external-source-absorption]
framework_mappings:
  quant:
    factor_type: [quality]
    pipeline_stage: [data, scoring, fusion, backtest]
  biopharma:
    pipeline_stage: [ml_screening, design, simulation, wetlab]
    therapy_type: [peptide, lnp, gene]
---

# 🧬 PENdp AI辅助多肽设计平台 — 索引 / 触发

> **⚠️ 代码先行 (2026-05-13)**  
> 本项目所有领域知识已移植为可运行 Python 包 `pendp`。  
> **本 Skill 不包含评分/数据库/管线数据** — 这些在代码中，且更新更快。  
> 调用 `pendp` 之前读 PROJECT_STATE.md 获取最新状态。

## 快速入口

**📘 14维评分系统完整说明**: `references/scoring-whitepaper-20260527.md` — 每维度的设计动机/评分公式/输出示例。<br>
**📊 HTML 演示 Deck（推荐浏览）**: `~/PENdp/pendp_deck_v4.html` — 键盘←→翻页，15页图文排版。

```bash
cd ~/.hermes/workspace/PENdp
pip install -e .  # 一次性安装

pendp info                     # 平台概览 + 各模块状态
pendp literature                # 文献数据库
pendp literature --semantic Q   # 🔍 语义搜索文献+序列
pendp search Q                  # 同上 (别名)
pendp decision --pipeline       # 管线优先级
pendp competition               # 竞争格局
pendp score --seq CRGDKGPDC     # 规则评分 (general模式, 默认)
pendp score --seq CHAIYPRH --mode brain  # 脑靶向评分模式 (D13激活)
pendp score --seq X --gates       # 🔬 V4: 门控评分 (PASS/FAIL/COND)
pendp score curated --seq iRGD   # 参考评分 (88.6)
pendp score curated --brain      # 全库脑靶向排序

**湿实验数据归档**: 见 `references/wetlab-archival-workflow.md`
**AA-LNP/ELP-LNP结题报告 (2026-05-22)**: `pendp/wetlab/data/2026-05-22_ADDS-YG-mRNA-LNP-1_结题报告.md` — 积雪草酸替代CHOL验证+ELP替代PEG验证+小鼠安全性数据
**PILs/AA-LNP对比分析 (2026-05-22)**: `pendp/literature/texts/2026-05-22_PILs_AA-LNP_对比分析.md` — 欣肽AA-LNP vs Nat Commun 2020(胆固醇类似物筛选) vs Nat Mater 2026(北大程群PILs)三方对标

**GitHub**: https://github.com/AlexJCD2025/PENdp-peptide-design (代码审查用)

### 打包交付（给审查员/外部合作者）

```bash
cd ~/.hermes/workspace
tar czf /tmp/PENdp_AI_Peptide_Design_v1.0.tar.gz \
  --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='.git' --exclude='models' --exclude='*.egg-info' \
  PENdp/
```

不含 `models/` 目录（MLX 嵌入模型 ~3GB 留在本地），审查员只需代码逻辑。

**完整用法:** `pendp --help` 或 `cat pendp/cli.py | grep "add_parser"`  
**项目状态:** `PROJECT_STATE.md` 在项目根目录

## 触发条件

用户提到以下任何关键词时加载此skill：
- PENdp / 欣肽 / 多肽设计 / 多肽靶向 / 多肽修饰
- 积雪草酸 / Asiatic Acid / ELP-LNP
- 肺靶向 / Lung Targeting / iRGD / iNGR
- 蛋白冠 / Protein Corona / CendR
- BreezeBio / ReCode / SORT LNP
- RP-832c / CD206 / IPF / 肺纤维化
- AKPC / p32
- 管线决策 / 适应症优先级
- **ASBT / 胆汁酸通路 / 胆汁酸转运体 / 胆酸偶联**（欣肽另一条口服多肽管线）
- **PLGA口服 / 口服PLGA纳米粒**（同上）
- **PepT1 / 口服多肽转运体**（负向触发 — 当用户说"不是PepT1路径"时，大概率指欣肽的ASBT-PLGA路线）
- **多肽质量控制 / 多肽QC争议 / 多肽检测不到 / 多肽不显色**（触发质控争议排查参考）
- **ELP / 弹性蛋白样多肽 / DMG-ELP / 程义云 / 替代PEG / ELP-LNP**（触发ELP-LNP设计原理查阅 — 见 `references/elp-lnp-mechanism-20260527.md`；文献核实见 `references/cheng-yiyun-elp-lit-verification-20260529.md` — 原引用的程义云ELP论文经全文核实均不成立）
- **多肽质量控制 / 多肽QC争议 / 多肽检测不到 / 多肽不显色**（触发质控争议排查参考）
- **6R / 阳离子多肽 / Poly-Arg / 肺靶向机制 / 蛋白冠肺靶向 / SORT LNP**（触发蛋白冠介导的内源性肺靶向机制调研）
- **DSPE-PEG-Maleimide / Cys偶联 / 多肽-LNP连接 / 偶联化学**（触发多肽LNP偶联设计讨论）
- **Ponceau S / 丽春红 / NC膜不显色 / 短肽检测**（触发短肽检测方法学匹配排查）
- **多肽溶解度 / 多肽复溶 / 多肽不溶**（触发复溶方案建议）
- **多肽溶解度 / 多肽复溶 / 多肽不溶**（触发复溶方案建议）
- **iCVETide / 诺和晟泰 / STC009 / CaSR 多肽**（触发竞争对标分析）
- **PENdp 优化 / AF3 / MD模拟 / QSAR / 分子对接 / 结构预测**（触发 iCVETide 驱动优化路线图）
- **多肽方法学论文 / JMC / 计算湿实验闭环**（触发论文路线图）
- **多肽合成 / SPPS / 固相合成 / Fmoc**（触发SPPS合成方案查阅 — 见 `references/4peptide-spss-synthesis.md`）
- **偶联方案 / LNP偶联 / 环化偶联 / DSPE-PEG / Maleimide**（触发环化多肽偶联机制查阅 — 见 `references/cyclic-peptide-lnp-conjugation.md`）
- **T7 / iRGD环化 / iRGD线性 / 6R / 脑靶向肽 / 肺靶向肽**（触发对应序列的SPPS合成方案查阅 — 见 `references/4peptide-spss-synthesis.md`）

## 核心架构 (代码中)

> ⚠️ **此架构描述PenDP N-Tab管线**。欣肽生物还有一条独立的**ASBT-PLGA口服多肽管线**（胆汁酸通路），详见下方"欣肽管线全景"章节。

```
三层技术协同:
  积雪草酸 (膜融合增强 → 内体逃逸)
    → ELP-LNP (蛋白冠 → 受体介导内吞)
    → 多肽修饰 (精准靶向, 最小化 off-target)

五关漏斗:
  [1] ML广筛 + ESM-2 + 评分  →  [G1-G12 Gate Pipeline 🆕 V4.3]  →  [AF3/MD/QSAR Pipeline 🆕 V4.4]  →  [5] 湿实验闭环

十二大评分维度 (V4.4, 权重总和1.0, 条件激活D13):
  D1 靶向基序(20%)  D2 物化性质(13%→10.5%)  D3 积雪草酸协同(7%)
  D4 蛋白冠+LNP(20%→17.5%) D5 Off-target(9%) D6 合成可行性(5%)
  D7 ESM相似度(2%)  D9 偶联定向性(5%)
  D10 ADMET/药化过滤(7%)  D11 糖基化影响(5%)
  D12 安全窗口/毒性风险(7%)  🆕 — Lipid-392启发
  D13 脑靶向评估(0%/8%)  🆕 V4.3 — 条件激活: 默认weight=0, --mode brain时weight=8%
  D14 结构可信度(5%,已激活)  🆕 V4.4 — ESMFold+MD+QSAR全管线已上线。pLDDT多级阈值:>70→3分,>50→1.5分,>30→0.5分(IPA补丁后均值~60→)。MD基于OpenMM(NPT 1ns,RMSD稳定性判定)。QSAR基于RDKit(三级ADMET过滤+pIC50预测)。D14_WEIGHT=0.05定义于config.py单源,D2/D4各借2.5%。激活验证28/28通过,reweight后总和1.0。

十二门门控 (G1-G12):
  G1(CRITICAL) G2(CRITICAL) G3(nice) G4(CRITICAL)
  G5(IMPORTANT) G6(IMPORTANT) G7(nice) G8(nice)
  G9(IMPORTANT) G10(nice) G11(IMPORTANT)  G12(IMPORTANT brain/NO general)  🆕脑靶向门
  → 7 CI gates: G1,G2,G4 + G5,G6,G9,G11 + G12(brain mode)

五大靶向子系统:
  肺/脑/肝/脾免疫/心肾  — 用 `pendp decision --subsystems` 查看
  
管线优先级 (代码内决策):
  IPF 🥇 | IMLD/MMA 🥈 | ADPKD | HCC  — 用 `pendp decision --pipeline` 查看
```

### 脑靶向子系统（新增 V4.3）
2026-05-26 基于LNP多肽修饰序列库 + T7/RVG29分析上线。

```bash
pendp score --seq CHAIYPRH                        # general模式（D13权重=0%）
pendp score --seq CHAIYPRH --mode brain            # 脑靶向模式（D13权重=8%）
pendp score curated --brain                         # 全库脑靶向排序
```

**架构设计**: D13注册在引擎中但默认weight=0，仅在`--mode brain`时激活。
D1(20→18%)和D4(20→18%)各让出2%给D13(8%)，权重守恒1.0。
门控G12在general mode下为NICE_TO_HAVE（不影响任何序列），brain mode下升为IMPORTANT。

详见 `references/brain-targeting-literature.md` 和 `references/lnp-peptide-library-20260526.md`。
详见 `/tmp/brain-dimension-architecture-decision.md`（完整ADR记录）。

## 关键历史教训 (不在代码中)

| 教训 | 来源 | 适用场景 |
|:-----|:-----|:---------|
| **代码先行** — Skill 不存领域数据，全部在 `pendp` 包 | 2026-05-13 融合时发现双重维护成本 | 所有 Code+Doc 项目 |
| **疾病中心** > 多肽中心 — 先选病再选肽 | 2026-05-03 新文档引入 | 管线决策 |
| **新信息冲击 → 认知升级四步** (提取→冲击→融合→落地) | 同上 | 收到外部新文档时 |
| **评分验证暴力搜索** — D4 是30%合并维度不是15%+15% | 2026-05-03 校准 | 评分系统权重定稿 |
| **AKPC=KPSSPPEE** (AKPC是缩写, 非序列本身) | 2026-05-13 Jarvis档案 | 文献引述 |
| **AKPC 靶点校正**: CD44 (非p32/原p32有误), A6肽(KPSSPPEE)靶向CD44, 年份2025 (非2024), 作者Zhao et al. | 2026-05-13 全文本获取发现(Zhao et al. ACS Nano 2025) | 查询/引用AKPC文献时 |
| **MOLEA 发表**: Nature Biotech 2026 (非bioRxiv 2025) | 同上 | 引用论文时 |
| **ASSET Protocol**: Veiga et al. 2018 (非2025) | 同上 | 引用论文时 |
| **残基计数Bug (V2→V4)**: `sum(1 for aa in "AVILMFWY" if aa in seq)` 统计的是残基**类型数**而非**频数**。`AAAAAAAAAA`=1个疏水而非10个。影响D2/D3/D4/D6/structure.py。修复: `sum(1 for aa in seq if aa in "AVILMFWY")` | 2026-05-15 Codex审计发现 | 所有评分计算 |
| **Gate校准全局污染 (V4)**: `calibrate()` 直接改共享 `PENDP_GATES` 列表中的 `GateDef.pass_threshold`。修复: `__init__` 中 deep-copy 门定义 | 同上 | 并发/复现 |
| **Cys重复惩罚 (V4→V4.1)**: 新增D10的Cys检测后旧代码未删除→奇数Cys被双重计数。修复方法: 新Cys检测替换旧位置,删除原`# Unpaired Cys count`块。 | 2026-05-16 Codex审查修bug时发现 | 涉及Cys计分的修改 |
| **D2/D10重叠风险**: D2(物化性质)已惩罚疏水/电荷聚集,D10(PAINS)再惩罚CC/WW/FF/多Cys→可能重复扣分。验证矩阵见 `references/v4.1-overlap-matrix.md`。D2/D10同<5方为真重叠。 | 同上 | 评分函数修改 |
| **Codex审计总分 5/10**: 见 `references/codex-audit-2026-05-15.md` | 同上 | V4 质量评估 |
| **脑靶向维度条件注册 (V4.3)**: D13不能直接以8%权重加入通用评分——非脑靶向肽(iRGD等)会被压低2-5分。解决方案: D13默认weight=0, `--mode brain`时激活, 从D1/D4各借2%。门控G12也是条件注册(general→NICE_TO_HAVE, brain→IMPORTANT)。总代码改动~130行, 5文件。 | 2026-05-26 达哥提出"影响整个系统吗" | 新增评分维度设计 |
| **Ponceau S/NC膜短肽检测假阴性**: 客户投诉多肽体外实验看不到Ponceau S斑点时，根因99%是短肽(1-3kDa)无法被NC膜有效保留+Ponceau S染色不敏感。MS+HPLC是行业放行标准，不验证下游应用功能。三段式回复: 技术解释→替代方案(LC-MS)→后续协助。详见`references/ponceau-s-small-peptide-troubleshooting.md` | 2026-05-26 朱鹤老师实际投诉 | 客户技术争议处理 |
| **D14 条件激活→已激活 (2026-05-27)**: D14权重改为5%固定,D14_WEIGHT单源定义在config.py,所有模块从此导入,消除三处重复定义。orchestrator.py Stage2-4从stub替换为integration.py真实调用(Stage2→ESMFold粗筛,Stage3→MD过滤,Stage4→D14终排)。回归测试覆盖5条肽段89项检查全部通过。详见`references/d14-architecture.md` | 2026-05-27 全管线端到端测试+Codex审查后架构整合 | D14/管线设计 |\n| **ESMFold IPA 补丁**: `pretrained.py` RuntimeError→KEY_REMAP修映射旧IPA键名至esm v2.0.0新键名,正确加载权重(norm=57.5))。短肽(<50aa) IPA贡献有限但pLDDT从40-46提升至~60。详见 `references/esmfold-installation-guide.md` | 2026-05-27 模型权重加载失败×2后root cause修复 | ESMFold 环境配置 |\n| **Codex 审计发现 19 项问题 (2026-05-27)**: 4 CRITICAL(pLDDT dict→float类型不匹配×2、字段key不对应×3、D14权重未加入dict、硬编码路径) + 7 WARNING + 8 INFO。修复覆盖 7 文件(integration/d14_integration/config/engine/__init__/orchestrator/af3_runner)。最严重bug: integration.py Stage 1 从predict_structure()读取不存在field→KeyError崩溃。根因: Codex生成大型多文件系统时对输出schema的假设与实际代码不匹配。修复: 全部改为从实际输出dict取值(mean提取/backend/runtime_seconds)。详见 `references/esmfold-installation-guide.md` | 2026-05-27 端到端管线测试失败后审计 | Codex生成多文件系统的验证流程 |\n| **D14 条件激活决策 (2026-05-27)**: 用户反馈\"全是0\"后变更设计——D14从固定5%改为默认weight=0条件激活。根因: pLDDT对短肽(<20aa)系统性偏低(IPA零初始化+训练数据偏差),MD/QSAR是stub,D14实际贡献近乎0。方案: D14保留在架构中weight=0.0,MD/QSAR从stub→真实模型后重新评估是否永久激活。pLDDT阈值从单一>70改为多级(>70→3分,>50→1.5分,>30→0.5分)以提高短肽区分度。详见 `references/d14-threshold-rationale.md` | 2026-05-27 用户反馈后架构决策 | 新增评分维度设计 |
| **ESMFold backend check false positive** — `check_esmfold_available()` 仅校验 `import esm`，不校验模型权重是否已缓存(~6GB)。需手动预下载 `esm.pretrained.esmfold_v1()` 才能实际运行。只有一种模型大小(3B参数)，无"小版本"。详见 `references/esmfold-installation-guide.md` | 2026-05-27 后台进程失败 & 用户追问模型大小 | ESMFold 模型预先下载 |
| **后台进程用系统Python 3.9**: Hermes的`terminal(background=True)`默认用`/usr/bin/python3`(macOS系统3.9.6)，不是venv的3.11.14。esm/torch装在venv里所以import失败。修复: 显式传完整路径 `/Users/aj/.hermes/hermes-agent/venv/bin/python3` | 2026-05-27 后台进程三次失败后根因分析 | 所有后台Python任务 |
| **文献引用必须全文+作者双重核实** — 原`elp-lnp-mechanism`参考文档将两篇论文归为程义云ELP工作。Adv. Sci. 2025全文核实0次提及ELP；JCR 2025作者核实为华中科技大学非程义云。影响：错误归因传播入技能触发条件和竞争对标章节。修复：新增核实报告+更新原文档+修正SKILL.md触发条件。 | 2026-05-29 文献审计链触发 | 所有外部文献引用 |

## 搜索模块 (语义)

```bash
pendp search "肺纤维化LNP靶向多肽" -k 5       # 文献+序列混搜
pendp search "RGD多肽LNP修饰" --full           # 完整字段
pendp literature --semantic "抗体修饰LNP"       # 文献中搜索
```

- 引擎: `jina-embeddings-v5-omni-small-retrieval` MLX 本地推理 (1.57B, 1024-dim)
- 覆盖: 7篇论文全文 (6/7已获取) + 13条肺靶向序列 (20条文档, ~0.7s建索引)
- 搜索质量: 全文索引后相似度从~0.1 → 0.5+
- 模型文件: `~/.hermes/workspace/PENdp/models/jina-embeddings-v5-omni-small-retrieval-mlx/` (~3 GB)
- 全文存储: `pendp/literature/texts/paper_{1-7}.txt`
- 详细集成: 见 `references/search-engine-integration.md`

### 已发现文献元数据修正

| 原数据 | 问题 | 修正后 | 发现方式 |
|:-------|:-----|:-------|:---------|
| AKPC靶点=p32, 年份=2024 | 实际靶点CD44, 年份2025 | Zhao et al. ACS Nano 2025 | 全文获取验证 |
| MOLEA=bioRxiv 2025 | 已正式发表 | Nature Biotech 2026 | 全文获取验证 |
| ASSET Protocol=2025 | 原始论文2018 | Veiga et al. Nature Comms 2018 | 全文获取验证 |
| paper_1付费墙无全文 | Nat Rev Drug Discov | 仅摘要可用 | 获取尝试失败 |
| 程义云ELP论文归因 | Adv. Sci. 2025归为ELP工作 | **0次提到ELP**，标准DMG-PEG配方 | PMC全文69K字核实 |
| 程义云ELP论文归因 | JCR 2025归为程义云工作 | **作者Li Fei等(HUST)**，非程义云 | PubMed作者+单位核实 |

**PILs/AA-LNP对比分析 (2026-05-22)**:
| 文献 | 来源 | 与PENdp关联 |
|:-----|:-----|:-----------|
| Nat Commun 2020 | 天然胆固醇类似物筛选 | AA属于Group III五环三萜，10%替代合理 |
| Nat Mater 2026 (程群/北大) | 多肽可电离脂质PILs | 多肽功能化LNP的器官靶向策略 |
| SciDirect 2024 | 科罗索酸完全替代CHOL | AA同分异构体，可完全替代胆固醇 |
详见 `pendp/literature/texts/2026-05-22_PILs_AA-LNP_对比分析.md`

**⚠️ 关键概念更新 (2026-05-22)**: 北大苗蕾(Nat Commun 2025)证明熊果酸(UA)作为"第五组分添加"(20%)而非替代CHOL, 实现40倍mRNA转染提升, 机制为V-ATPase激活。这颠覆了Nat Commun 2020"五环三萜效果差"的结论——"替代"与"添加"是两种完全不同的策略。对欣肽AA-LNP的直接启示: 应尝试AA作为第五组分添加(而非替代CHOL)。详见 `pendp/wetlab/references/2026-05-22_LNP_对比分析_BioBlue.pdf`
详见 `references/paper_metadata_corrections.md`
**PILs/AA-LNP文献索引**: `references/pils-aa-lnp-literature-index.md`
**AA-LNP综合研发报告 v3.1**: `~/brain/reports/AA-LNP-comprehensive-analysis-20260522.md` — 实验数据+文献对标+PILs分析+专利策略
**LNP-多肽修饰序列库 (2026-05-26)**: `references/lnp-peptide-library-20260526.md` — 13条DSPE-PEG-肽修饰序列(HA2内体逃逸/CD47免疫逃逸/电荷靶向等), 与PenDP序列库对比参考
**AA&ELP-LNP湿实验 (2026-05-26)**: `pendp/wetlab/data/2026-05-26_AA-ELP-LNP-vs-CHOL-LNP.md` — AA部分替代CHOL，包封率94% vs 92%，损失率28.4% vs 42.3%（AA显著降低制备损失）\n**ELP-LNP vs AA-LNP单独对照 (2026-05-27)**: `pendp/wetlab/data/2026-05-27_ELP-LNP-vs-AA-LNP.md` — ELP-LNP损失率22.5%（历史最低），AA-LNP损失率38.5%，确认ELP替代PEG是降低损失率的关键变量。详见 `references/elp-lnp-mechanism-20260527.md`

**⚠️ 关键概念更新 (2026-05-22)**: 北大苗蕾(Nat Commun 2025)证明熊果酸(UA)作为"第五组分添加"(20%)而非替代CHOL, 实现40倍mRNA转染提升, 机制为V-ATPase激活。

详见 `references/paper_metadata_corrections.md`

## 竞争对标 & 行业参考

- PeptAI (BIO Protocol): 自治多肽发现 Agent，8+1 串行验证门 (G0-G9)，湿实验闭环 (x402)。
  完整对标分析见 `references/peptai-benchmark.md`。
  - PENdp 可借鉴: 门控决策层 (PASS/FAIL/COND) + 结构预测管线 (AlphaFold/Boltz)
  - PENdp 优势: 自研评分框架 + 递送系统深度 + 无代币叙事风险
  - **🆕 V3已落地**: Gate Pipeline 上线，详见 `references/gate-design.md`
- **6R/阳离子多肽肺靶向机制** — 蛋白冠介导内源性靶向（2026-05-27调研）：
  - 6R(RRRRRR)的肺靶向不依赖受体配体识别，通过 **正电荷→招募Vitronectin/Fibrinogen(RGD蛋白)→αvβ3整合素→肺内皮捕获** 的三步间接机制
  - 与SORT LNP(DOTAP)的肺靶向机制一致（PNAS 2021, Dilliard et al.）
  - Vitronectin是肺靶向的核心内源性配体（J Control Release 2023）
  - 详见 `references/6R-protein-corona-mechanism-20260527.md`
  - **对评分的启示**：D4(蛋白冠)→6R高分是正确的；D1(靶向)→6R低分也是正确的（靶向来自蛋白冠而非序列本身）；D10/D12→6R低分已捕获Fibrinogen招募带来的凝血风险

**iCVETide® / 诺和晟泰 STC009（2026-05-27 新增）**：
  - 论文：*Discovery of CaSR Peptide Agonists via Multistage Screening* (J. Med. Chem. 2025, 中科院 1 区 TOP)
  - 平台：iCVETide® 深度融合 CADD + AI，覆盖分子对接→动力学模拟→自动化多肽合成→生物学评价全流程
  - 策略：关键残基替换（key residue replacement）增强结合亲和力 → 多级筛选
  - 管线：STC009（CaSR 多肽激动剂）→ PCC → GLP 安评 → 2026Q1 申报临床
  - **对标启示**：
    1. 🔴 **AF3/MD/QSAR stub 是最大差距** — iCVETide 的分子对接+MD全流程已跑通并产出 PCC，PENdp 这三个 stub 需要补上
    2. 🟢 关键残基替换策略与 PENdp 的多肽修饰逻辑一致，但 iCVETide 将其方法学化并发了 JMC
    3. 🔴 缺乏方法学论文 — iCVETide 证明了 CADD+AI 驱动多肽发现→顶刊→PCC/GLP 的路径可行
    4. 🟡 已验证靶点+新分子类型策略与 PENdp 一致
    5. 详见 `references/icvetide-novosuntide-benchmark-20260527.md`
    6. **iCVETide 驱动优化路线图** 详见 `references/icvetide-optimization-roadmap-20260527.md`（P0: AF3/MD/QSAR stubs → P1: 湿实验闭环 → P1: 方法学论文）
- **多肽-LNP偶联设计（2026-05-27）**：T7(HAIYPRH) / iRGD(CRGDKGPDC,环化) / iRGD-L(线性) / 6R(RRRRRR) — 四种序列的LNP偶联设计与合成方案，详见 `references/4peptide-conjugation-designs-20260527.md`\n- **ELP替代PEG的LNP设计原理（2026-05-27，⚠️ 2026-05-29文献核实更正）**：原文档将两篇论文归为程义云ELP工作，经全文下载+作者验证：①Adv. Sci. 2025(Ren/Cheng)全文0次提及ELP ②JCR 2025(Li et al.)为华中科技大学工作，非程义云。**目前没有已发表的ELP替代PEG文献**。欣肽ELP-LNP数据（损失率22.5%历史最低）为原始发现。详见 `references/elp-lnp-mechanism-20260527.md` 和 `references/cheng-yiyun-elp-lit-verification-20260529.md`\n- **方法学论文（2026-05-26）**：PENdp发表目标——对标iCVETide的JMC路径

## 欣肽生物管线全景 — 两条独立的口服多肽路线

欣肽生物有**两条平行口服多肽递送管线**，技术路线完全不同：

| 管线 | 递送机制 | 载体 | 靶点/路径 | 状态 |
|:-----|:---------|:-----|:----------|:-----|
| **PenDP N-Tab** 🧬 | 蛋白冠介导受体内吞 → 内体逃逸 | AA+ELP+LNP | 未公开（非PepT1，非ASBT） | DLS表征完成，评分系统V4.2 |
| **ASBT-PLGA** 💊 | 胆汁酸转运体介导内吞 | 胆酸修饰PLGA纳米粒 | **ASBT (SLC10A2)** — 回肠顶端钠依赖性胆汁酸转运体 | 项目管理阶段，文献调研中 |

**关键区别**:
- PenDP N-Tab 走蛋白冠/受体介导内吞（化学纳米），不等同于胆汁酸通路
- ASBT-PLGA 走肠道内源性胆汁酸回收通路（**不是PepT1，也不是N-Tab的路径**）
- 两条管线是**独立的平行探索**，不要混为一谈

**常见错误**（本skill的历史踩坑）:
- ❌ 以为欣肽的全部口服多肽技术就是PenDP N-Tab → PenDP只是其一
- ❌ 以为ASBT=某种LNP修饰 → ASBT是通过胆酸偶联激活的跨膜转运体，机制完全不同
- ❌ 混淆ASBT与PepT1 → ASBT在回肠表达，PepT1在十二指肠/空肠，两者是不同转运体家族

详见 `references/asbt-bile-acid-oral-delivery.md`。

## 🏭 口服生物药递送技术路线分类 (2026-05-22)

PenDP的N-Tab路线属于**化学纳米递送**。理解它与**机械物理递送**和**胆汁酸通路递送**路线的结构性差异，对管线决策和竞争定位至关重要。

### 三大哲学

| 路线 | 代表 | 核心逻辑 | 典型机构/项目 |
|:-----|:-----|:---------|:-------------|
| **机械物理** | 可吞服机器人胶囊 | **绕过**吸收屏障（物理穿刺/注射） | RaniPill(Rani Therapeutics), Entera(EB613) |
| **化学纳米** | 纳米颗粒 + 靶向修饰 | **穿过**吸收屏障（受体介导内吞） | PenDP N-Tab, BreezeBio, ReCode |
| **胆汁酸通路** | 胆酸偶联PLGA/载体 | **搭便车**通过内源性转运体（ASBT介导内吞） | **欣肽ASBT-PLGA** |

### 核心差异矩阵

| 维度 | 机械物理 | 化学纳米 (PenDP N-Tab) | 胆汁酸通路 (ASBT-PLGA) |
|:----|:---------|:----------------------|:----------------------|
| **Bioavailability** | **高**（可接近注射，RT-102达300-400%） | **低-中**（典型口服LNP 1-20%） | **中**（文献benchmark 15-20%） |
| **药物通用性** | 极强 — 任何大分子药都能搭载 | 中等 — 需适配LNP包封条件 | 中等 — 需胆酸偶联能力 |
| **临床验证深度** | I期完成（Rani RT-102, 90%+递送成功率） | DLS表征阶段（~80-95nm, PDI~0.26） | 主要在动物阶段，无人临床 |
| **器械复杂度** | 高 — 可溶针+化学反应+气球+pH触发 | 中 — 微流控合成+冻干 | 中 — PLGA纳米粒制备（成熟工艺） |
| **长期安全性** | 未知 — 反复针刺肠段累积效应 | 高 — LNP亿级剂mRNA疫苗数据背书 | 中高 — PLGA是FDA批准材料（注射/植入），但口服PLGA数据有限 |
| **监管路径** | 组合产品（drug-device），审批更复杂 | 单一NDA（505(b)(2)），更简洁 | 单一NDA（505(b)(2)），PLGA有先例 |
| **规模成本** | 每粒精密胶囊组装成本高（估计>$5/粒） | 微流控合成可放大到<$1/剂 | PLGA纳米粒生产成本中等 |
| **患者体验** | 吞咽大胶囊（~2cm，可能有异物感） | 正常口服 | 正常口服 |

### 对PenDP的战略启示

机械物理路线的Bioav高是**物理作弊**（针扎肠壁），化学纳米路线在纯bioav上打不过它。但PenDP N-Tab在三个维度有结构性优势：

1. **安全性差异巨大** — 每周/每天吞带针胶囊持续1-2年，长期GI安全性未知。LNP临床安全性数据库是亿剂级的（mRNA疫苗）
2. **成本结构根本不同** — 精密胶囊很难降到<$5/粒，LNP微流控合成大规模可到<$1/剂
3. **递送精度** — 机械路线是"盲扎"（pH触发后自动穿刺，不知道扎在哪儿）；N-Tab可设计靶向特定肠段受体，理论上可精准控制吸收位置

**关键判断**: Rani Therapeutics的管线转舵（RT-102口服PTH搁置 → RT-114 GLP-1/GLP-2双激动剂）说明口服生物药市场竞争已进入拥挤阶段——即使RaniPill有Bioav优势，仍受限于现金跑道被迫追GLP-1热点。PenDP的差异化应在**靶向性+安全性+成本**，而非追求极致bioav。

**内部平行管线关系**: ASBT-PLGA作为第二条口服路线，与N-Tab是探索不同科学路径的互补关系。ASBT路线的文献benchmark（15-20% bioav）可作为N-Tab的参照目标，但两者机制不同，不应直接比较。

详见 `references/oral-biologics-delivery-landscape.md`。
**口服多肽 & GLP-1全景 (2026-05-26)**: `references/oral-peptide-glp1-landscape-20260526.md` — 市场规模、竞争格局、四大技术路线对比(SNAC/ASBT/PLGA/机械物理)，SNAC技术分析，对欣肽ASBT-PLGA的定位参考

## 🧬 K-Dense 科学技能集成 (V4.1 — 2026-05-16)

从 [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) (21.8k⭐, 137 skills) 集成第一批13个技能到 `~/.hermes/skills/`。

**PENdp 代码内集成:**
- `D10` (7%) ADMET/药化过滤 — `score_medchem_filter()` in `pendp/scoring/engine.py`
- `D11` (5%) 糖基化影响 — `score_glycoengineering()` in `pendp/scoring/engine.py`
- `G9` (IMPORTANT) + `G10` (nice) — in `pendp/scoring/gates.py`
- `can_proceed()` 动态CI计数 — 不再硬编码 `ci_total=5`

**已安装的科学技能文档 (全部13个):**
| 域 | 技能 | 位置 |
|---|---|---|
| 生物医药 | deepchem, rdkit, datamol, pytdc, medchem, diffdock, glycoengineering, esm | `biopharma-framework/` |
| 量化 | aeon, pymoo | `data-science/` |
| 研究 | database-lookup, autoskill, hypogenic | `research/` |

> D10/D11 当前为规则版实现 (零外部依赖)。后期可用 deepchem/rdkit 升级为分子级预测。  
> D2/D10 重叠测试矩阵见 `references/v4.1-overlap-matrix.md`。  
**脑靶向文献缺口见 `references/brain-targeting-literature.md`。
**多肽质控争议排查**: `references/peptide-qc-dispute-resolution.md` — 客户反馈多肽"检测不到"时的系统排查漏斗（Ponceau S假阴性、短肽膜保留、复溶问题、验证实验优先级）
- **环化多肽-LNP偶联机制** — 见 `references/cyclic-peptide-lnp-conjugation.md`（三策略详解 + D9评分逻辑对照 + 真实案例）

<!-- curator-evolver:auto:start -->
## Auto-curated evidence notes

Low-risk bounded auto-curation generated by `hermes-curator-evolver`.
These notes are evidence summaries for future agents; they do not replace human-authored SOPs.

- Skill: `pendp-peptide-design`
- Generated at: `2026-05-29T10:28:33+00:00`
- Evidence window: last 7 day(s)
- Tool events: 168
- Skill events: 168
- Error-like events: 20

### Recent evidence
- 2026-05-29T16:11:30+00:00: `skill_view` ok — {"success": true, "name": "pendp-peptide-design", "description": "PENdp AI辅助多肽设计平台 V4.4 — 积雪草酸+ELP-LNP+多肽修饰三层协同。含12+1维评分(D13条件激活脑靶向+D14结构可信度)+12门串行门控、AF3/MD/QSAR管线、肺靶向数据库v6、ESM-2语义搜索、竞争对标、管线决策框架", "tags": ["pendp", "pep…
- 2026-05-29T16:11:30+00:00: `skill_view` ok — {"success": true, "name": "pendp-peptide-design", "file": "references/elp-lnp-mechanism-20260527.md", "content": "# ELP替代PEG的LNP设计原理\n\n**调研日期**: 2026-05-27\n**来源**: 程义云（华东师范大学生命科学学院）课题组\n\n## 核心洞察\n\nELP（弹性蛋白样多肽）替代DMG-…
- 2026-05-29T16:11:30+00:00: `skill_view` ok — {"success": true, "name": "pendp-peptide-design", "file": "references/elp-lnp-mechanism-20260527.md", "content": "# ELP替代PEG的LNP设计原理\n\n**调研日期**: 2026-05-27\n**来源**: 程义云（华东师范大学生命科学学院）课题组\n\n## 核心洞察\n\nELP（弹性蛋白样多肽）替代DMG-…
- 2026-05-29T16:11:30+00:00: `skill_view` ok — {"success": true, "name": "pendp-peptide-design", "description": "PENdp AI辅助多肽设计平台 V4.4 — 积雪草酸+ELP-LNP+多肽修饰三层协同。含12+1维评分(D13条件激活脑靶向+D14结构可信度)+12门串行门控、AF3/MD/QSAR管线、肺靶向数据库v6、ESM-2语义搜索、竞争对标、管线决策框架", "tags": ["pendp", "pep…
- 2026-05-29T16:11:30+00:00: `skill_manage` ok — {"success": true, "message": "Patched SKILL.md in skill 'pendp-peptide-design' (1 replacement)."}

### Agent guidance
- When this skill is relevant, check these observed signals before choosing a workflow.
- Prefer targeted verification over broad retries when similar errors recur.
- If a repeated issue is understood, replace this evidence note with a concise human-readable SOP update.
<!-- curator-evolver:auto:end -->
