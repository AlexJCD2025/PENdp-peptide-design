# PENdp 14维评分系统白皮书 (2026-05-27)

## 格式偏好 (达哥确认)

| 偏好 | 内容 |
|:-----|:------|
| **首选格式** | PPT风格横向滑页 Deck (HTML) — 键盘←→翻页，每页一章节 |
| **次选** | A4竖版 PDF (仅用于存档) |
| **禁止** | A4横版 PDF — 排版效果差（字小、留白多、对齐难） |
| **字号** | 标题 ≥28px, 正文 ≥15px, 表格 ≥13px, 代码 ≥12px |
| **配色** | 浅色主题: 白底 #fff, 浅蓝主色 #0ea5e9, 浅黄点缀 #f59e0b |
| **信息密度** | 宁可多分几页也不要塞太满，每页1-2个核心内容 |

## HTML Deck 标准

使用 `deck-simple` 技能生成:
- Print-oriented 变体 (A4 landscape + page-break) 可转PDF
- Screen-oriented 变体 (position:absolute + opacity) 纯屏幕演示
- 两者不可混用

## 已生成文件

| 文件 | 描述 | 位置 |
|:-----|:------|:-----|
| PENdp_14维评分系统设计白皮书.md | 完整14维评分设计文档 | PENdp/ |
| pendp_deck_v4.html | 15页交互式HTML Deck | PENdp/ |
| PENdp_14维评分系统_V4.pdf | 排版优化版PDF (14页) | PENdp/ |
