# jina-embeddings-v5-omni PENdp 集成指南

## 模型选型

| 指标 | Nano | Small (已选用) |
|:-----|:----:|:--------------:|
| 参数量 | 0.95B | **1.57B** |
| 向量维度 | 768 | **1024** |
| 模型文件大小 | 1.83 GB | **2.97 GB** |
| M5 Max 加载 | 0.1s | **0.2s** |
| 20条文档索引 | 0.4s | **0.7s** |

**结论**: 在 Apple Silicon M5 Max 上 small 性价比远高于 nano — 加载速度几乎一样，搜索质量提升明显。

## 安装

```bash
# 下载 small MLX 模型 (~3 GB)
cd ~/.hermes/workspace/PENdp
python3 -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='jinaai/jina-embeddings-v5-omni-small-retrieval-mlx',
    local_dir='models/jina-embeddings-v5-omni-small-retrieval-mlx',
)
"
```

## PYTHONPATH

搜索模块加载 model.py 时需要将模型目录加到 PYTHONPATH:

```bash
export PYTHONPATH="$HOME/.hermes/workspace/PENdp/models/jina-embeddings-v5-omni-small-retrieval-mlx"
```

或在 Hermes venv 下运行:
```bash
PYTHONPATH="..." ~/.hermes/hermes-agent/venv/bin/pendp search "query"
```

## 全文文件命名

```
pendp/literature/texts/paper_{1-7}.txt
```

- paper_1.txt: 肿瘤疫苗全景 (Nat Rev Drug Discov 2026, 付费墙 - 仅摘要)
- paper_2.txt: CendR穿透机制 (Frontiers/Ruoslahti 2013)
- paper_3.txt: AKPC-LNP (Zhao et al. ACS Nano 2025, ✅ 全文)
- paper_4.txt: RP-832c/CD206/IPF (已有元数据)
- paper_5.txt: MOLEA多目标优化 (Nature Biotech 2026, ✅ 全文)
- paper_6.txt: ASSET抗体LNP (Nature Comms 2018, ✅ 全文)
- paper_7.txt: NMPA审评报告 (CDE 2026)

## 已知局限

1. 全文搜索仅在 paper_{i}.txt 存在时启用；缺失则回退到元数据搜索
2. 仅英文 + 中文混合支持（jina-v5 原生支持中文）
3. 暂不支持图片/PDF直接向量化（v5-omni 支持该能力，需 encode_image 接口）
4. 截至2026-05-13: 模型 CC BY-NC 4.0，商业使用需授权
