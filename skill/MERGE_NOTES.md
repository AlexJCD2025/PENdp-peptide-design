# V4.4 Skill Bundle — Merge Notes

合并时间: 2026-06-14 · 合并到分支 `claude/ai-multimodal-code-review-f820ha`

## 这是什么

本 `skill/` 目录是 **PENdp V4.4 的知识/文档层**（Claude Skill 包），来自上传的
`PENdppeptidedesignv4.4` 压缩包，内容为：

- `SKILL.md` — 技能索引/触发文档（V4.4，权威的维度/门控说明）
- `references/` — 33 篇研究与文献笔记（脑靶向、ELP-LNP、ASBT、ESMFold、Codex 审计等）
- `scripts/` — 2 个**已归档**的旧评分脚本（akpc / rp832c），运行即打印 "已归档" 并退出
- `BUNDLE_README.md` — 压缩包自带的备份清单（见下方“已知问题”）

## ⚠️ 重要：这是文档，不是 V4.4 代码

该压缩包**不包含 V4.4 的 Python 实现**。SKILL.md 描述的 D10–D14 维度、G9–G12 门控、
brain 模式、`integration.py`/`af3_runner.py`/`d14_integration.py`、`config.py` 中的
`D14_WEIGHT` 等，**均不在本压缩包内**。

仓库里实际的 `PENdp/pendp/` 代码包仍停留在 **V4.1 水平**（D1–D9 八维 + G1–G8 八门）。
因此合并本文档层不会升级代码；文档（描述 14 维/12 门）与代码（8 维/8 门）目前不一致。
若要让 GitHub 代码达到 V4.4，需要单独提供/推送 `pendp` 包的 V4.4 源码。

## ⚠️ 已知问题：BUNDLE_README.md 的维度表是错的

`BUNDLE_README.md` 里的“14 维评分列表”（D1 序列合理性 / D2 二级结构倾向 / D3 溶解度 /
D4 蛋白酶稳定性 / D5 膜透过性 / D10 成本估算 / D11 知识产权 / D12 临床潜力 …）
**与真实系统不符**，且权重相加 ≈ 105%（非 1.0）。

权威定义见 `SKILL.md` 与 `references/d14-architecture.md`，并与仓库 `PENdp/pendp/config.py`
一致：D1 靶向基序 / D2 物化性质 / D3 积雪草酸协同 / D4 蛋白冠+LNP / D5 Off-target /
D6 合成可行性 / D7 ESM 相似度 / D9 偶联定向性 / D10 ADMET / D11 糖基化 / D12 安全窗口 /
D13 脑靶向(条件激活) / D14 结构可信度。BUNDLE_README.md 仅作原始备份留存，勿当作准确文档。

## 历史背景：之前为何 GitHub 上看不到 V4.4

压缩包 README 已确认：V4.4 向 GitHub 的推送**失败（401 Unauthorized）**——
`gh` CLI 的 OAuth token 不能用于 `git push` 的 HTTPS 认证。所以此前仓库一直停在旧版本。
