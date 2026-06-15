# 湿实验数据归档工作流

**目的**: 将 wet lab 实验数据（PPTX/MD 格式的实验报告）归档到 PenDP 追踪系统

## 步骤

### 1. 提取实验数据

实验报告通常来自 PPTX（DLS表征结果）或 MD 文档。用 `mcp-ppt` 读取 PPTX 内容。

关键字段:
- **配方**: 各组分浓度(mg/ml/mM)、Mn、体积(μL)
- **AA占比**: AA/(SM-102+AA) mol% 和 AA/(总脂质) mol%
- **两组条件**: 微流控流速对比（如 9 vs 32 ml/min）
- **DLS**: 粒径(nm)、PDI、电位(mV) — 透析前后对比、三重复
- **浓缩倍数**: 透析前体积/透析后体积
- **透析液**: 通常 10% 蔗糖 PBS

### 2. 创建实验记录文件

格式: `pendp/wetlab/data/YYYY-MM-DD_<实验描述>.md`

内容模板:
```
# <实验标题>

**实验日期**: YYYY-MM-DD
**对应管线任务**: WL-X (任务描述)
**保存路径**: pendp/wetlab/data/<文件名>

## 一、实验目的
...

## 二、配方
(表格形式: 组分/浓度/Mn/体积/摩尔量/摩尔比)

## 三、两组条件对比
(表格: 参数/条件A/条件B)

## 四、DLS 表征结果
(按条件分组, 表格: 样品/粒径/PDI/电位)
含重复、均值、标准差

## 五、结论
关键发现、最优条件

## 六、关联任务
- WL-X: 该实验对应的任务
- 下一步建议
```

### 3. 更新湿实验追踪器

修改 `pendp/wetlab/tracker.py`:

- 找到对应的 WL task
- 改 `status` 为 `in_progress` 或 `completed`
- 在 `notes` 中添加: `"YYYY-MM-DD: <实验摘要> | 数据: pendp/wetlab/data/<文件名>"`
- 如果涉及新任务, 在 WETLAB_PLAN 末尾追加

### 4. 保存原始文件

将原始实验报告（PPTX等）复制到数据目录:
```
cp <原始文件> pendp/wetlab/data/YYYY-MM-DD_<描述>.pptx
```

### 5. 验证

```python
from pendp.wetlab.tracker import WETLAB_PLAN
print(f"总计: {len(WETLAB_PLAN)} | 进行中: {sum(1 for t in WETLAB_PLAN if t.status=='in_progress')}")
```

## 管线状态解码

| 状态 | 含义 |
|:----|:-----|
| pending | 待执行 |
| in_progress | 进行中 |
| completed | 已完成 |
| blocked | 受阻 |

## 已实验数据

| 日期 | 实验 | 文件 |
|:----|:-----|:-----|
| 2026-05-20 | AA&ELP-LNP 首轮配方(9/32ml/min流速对比+DLS) | `data/2026-05-20_AA-ELP-LNP_formulation.md` (.pptx) |
