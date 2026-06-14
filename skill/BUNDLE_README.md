# 📦 PENdp-peptide-design v4.4 — 完整备份
**打包时间**: 2026-06-14 21:42
**版本**: 4.4.0 (基于 SKILL.md frontmatter, 实际更新 2026-05-29)
**源路径**: `~/.hermes/skills/biopharma-framework/pendp-peptide-design/`
**总大小**: 约 208 KB
**文件数**: SKILL.md + 33 references/ + 2 scripts/ = 36 个文件

---

## 核心能力 (V4.4)

**PENdp AI 辅助多肽设计平台 V4.4** — 积雪草酸 + ELP-LNP + 多肽修饰三层协同。
- **14 维评分系统** (12 基础 + D13 条件激活脑靶向 + D14 结构可信度)
- **12 门串行门控** (G1-G12, V4.3 起)
- **AF3 / MD / QSAR 管线** (V4.4 升级)
- **肺靶向数据库 v6**
- **ESM-2 语义搜索**

## 14 维评分列表

| 维度 | 名称 | 权重 | 状态 |
|------|------|------|------|
| D1 | 序列合理性 | 18% | 基础 |
| D2 | 二级结构倾向 | 15.5% | 基础 (V4.4 让 2.5% 给 D14) |
| D3 | 溶解度 | 10% | 基础 |
| D4 | 蛋白酶稳定性 | 15.5% | 基础 (V4.4 让 2.5% 给 D14) |
| D5 | 膜透过性 | 10% | 基础 |
| D6 | 代谢稳定性 | 8% | 基础 |
| D7 | 毒性预测 | 8% | 基础 |
| D8 | 合成可行性 | 5% | 基础 |
| D9 | 免疫原性 | 4% | 基础 |
| D10 | 成本估算 | 3% | 基础 |
| D11 | 知识产权 | 2% | 基础 |
| D12 | 临床潜力 | 1% | 基础 |
| **D13** | **脑靶向评估** | **0% / 8%** | **🆕 V4.3 条件激活** (--mode brain) |
| **D14** | **结构可信度** | **5%** | **🆕 V4.4 已激活** (ESMFold+MD+QSAR) |

**权重总和 = 1.0** (V4.4 守恒校验通过)

## D14 V4.4 新增说明 (重要)

**D14 结构可信度** = ESMFold + MD + QSAR 全管线:
- **ESMFold** pLDDT 多级阈值: >70 → 3 分 / >50 → 1.5 分 / >30 → 0.5 分 (IPA 补丁后均值 ~60)
- **MD** 基于 OpenMM (NPT 1ns, RMSD 稳定性判定)
- **QSAR** 基于 RDKit (三级 ADMET 过滤 + pIC50 预测)
- **D14_WEIGHT = 0.05** 定义于 `config.py` 单源, D2/D4 各借 2.5%
- **激活验证 28/28 通过**, reweight 后总和 1.0

## 调用示例

```bash
cd ~/.hermes/workspace/PENdp
pip install -e .  # 一次性安装

pendp info                     # 平台概览 + 各模块状态
pendp literature                # 文献数据库
pendp literature --semantic Q   # 语义搜索文献+序列
pendp search Q                  # 同上 (别名)
pendp decision --pipeline       # 管线优先级
pendp competition               # 竞争格局
pendp score --seq CRGDKGPDC     # 规则评分 (general 模式, 默认)
pendp score --seq CHAIYPRH --mode brain  # 脑靶向评分模式 (D13 激活)
pendp score --seq X --gates       # 🔬 V4: 门控评分 (PASS/FAIL/COND)
pendp score curated --seq iRGD   # 参考评分 (88.6)
pendp score curated --brain      # 全库脑靶向排序
```

## 目录结构

```
PENdp-peptide-design-v4.4-20260614/
├── README.md                      # 本文件
├── SKILL.md                       # 主索引文档 (30 KB)
├── references/                    # 33 个参考文档
│   ├── 2026-05-27-6R-protein-corona-mechanism.md
│   ├── 2026-05-27-ELP-PEG-replacement-mechanism.md
│   ├── 4peptide-conjugation-designs-20260527.md
│   ├── 4peptide-spss-synthesis.md
│   ├── 6R-protein-corona-mechanism-20260527.md
│   ├── asbt-bile-acid-oral-delivery.md
│   ├── brain-targeting-analysis-20260526.md
│   ├── brain-targeting-literature.md
│   ├── brain-targeting-sequence-analysis.md
│   ├── cellvq-weight-download.md
│   ├── cheng-yiyun-elp-lit-verification-20260529.md
│   ├── codex-audit-2026-05-15.md
│   ├── codex-audit-workflow.md
│   ├── cyclic-peptide-lnp-conjugation.md
│   ├── d14-architecture.md        # ← D14 架构设计
│   ├── elp-lnp-mechanism-20260527.md
│   ├── esmfold-installation-guide.md
│   ├── gate-design.md
│   ├── icvetide-novosuntide-benchmark-20260527.md
│   ├── icvetide-optimization-roadmap-20260527.md
│   ├── k-dense-integration.md
│   ├── lnp-peptide-library-20260526.md
│   ├── oral-biologics-delivery-landscape.md
│   ├── oral-peptide-glp1-landscape-20260526.md
│   ├── paper_metadata_corrections.md
│   ├── peptai-benchmark.md
│   ├── peptide-qc-dispute-resolution.md
│   ├── pils-aa-lnp-literature-index.md
│   ├── ponceau-s-small-peptide-troubleshooting.md
│   ├── scoring-whitepaper-20260527.md  # ← 14 维完整白皮书
│   ├── search-engine-integration.md
│   ├── v4.1-overlap-matrix.md
│   └── wetlab-archival-workflow.md
└── scripts/                        # 2 个评分脚本
    ├── akpc_v2_score.py
    └── rp832c_v2_score.py
```

## 版本历史

| 版本 | 日期 | 主要升级 |
|------|------|----------|
| **V4.4** | 2026-05-27 (skill) / 2026-05-29 (last mtime) | **D14 结构可信度** (ESMFold+MD+QSAR) / 12 门串行门控 / 肺靶向数据库 v6 |
| V4.3 | 2026-04 | D13 脑靶向 (条件激活) / 路径规划 3 阶段 |
| V4.2 | 2026-02 | 12+1 维评分 (D13 注册) / 12 门门控 |
| V1.0 | 2025-xx | 早期 demo (公开于 GitHub AlexJCD2025/PENdp-peptide-design) |

## 重要说明 (PUSH 失败)

**本次打包与 GitHub 推送无关**。达哥之前问 PenDP v4.4 是否最新 / 是否上传 GitHub:
- ✅ 本地 = V4.4.0 (最新)
- ❌ GitHub 推送 **失败 (401 Unauthorized)** — 因 `gh CLI` 的 OAuth token 不能用于 `git push` HTTPS 认证
- ⚠️ GitHub 现状: `AlexJCD2025/PENdp-peptide-design` 公开仓库描述仍为 v1.0, 未见 v4.4-current 分支

**本 ZIP = 离线完整备份**, 可直接拷贝到其他机器 / U 盘 / 邮件发送。
