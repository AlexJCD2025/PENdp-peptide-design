# PENdp AI Peptide Design Platform

PENdp = **多肽修饰LNP → 肝外靶向（肺）**

积雪草酸 + ELP-LNP + AI多肽设计 三位一体的靶向核酸递送平台。

## 技术架构：五关融合漏斗

```
【第一关】ML广筛 / ESM-2 + CPP → 候选序列(1000+)
【第二关】AlphaFold3 / 分子对接 → Top 50-100 (stub)
【第三关】MD动力学验证 → Top 20-30 (stub)
【第四关】QSAR/GNN精修 → 5-10条最终候选 (stub)
【第五关】湿实验闭环 → 数据回流训练
```

## 快速开始

```bash
cd ~/.hermes/workspace/PENdp
pip install -e .

# 查看所有命令
pendp --help

# 对序列进行评分
pendp score --seq CRGDKGPDC

# 运行完整管线
pendp pipeline --mode quick

# 查看数据库
pendp db list
```

## 核心模块

| 模块 | 功能 | 状态 |
|------|------|------|
| `pendp.esm` | ESM-2模型加载与嵌入（8M/35M/150M/650M） | ✅ |
| `pendp.scoring` | 7维度评分系统 v2.0 | ✅ |
| `pendp.cpp` | CPP分类器（ESM-2 + LR） | ✅ |
| `pendp.database` | 肺靶向v6数据库 + 靶点知识图谱 | ✅ |
| `pendp.lnp` | 积雪草酸LNP + 蛋白冠分析 | ⏳ |
| `pendp.pipeline` | 五关漏斗编排器 | ✅ |
| `pendp.cli` | CLI命令行入口 | ✅ |

## 文件结构

```
PENdp/
├── pendp/              # 主包
├── data/               # 数据库文件
├── tests/              # 测试
├── setup.py            # 安装配置
└── README.md           # 本文件
```
