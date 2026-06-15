#!/usr/bin/env python3
"""
⚠️ 已归档 — 由 pendp Python 包替代

此脚本已被 ~/.hermes/workspace/PENdp/pendp/scoring/engine.py 替代。
评分引擎 v2.0 的所有功能已集成到 `pendp` 包中。
保留仅作历史参考，不再用于实际分析。

使用方式 (新):
    pip install -e ~/.hermes/workspace/PENdp
    from pendp.scoring.engine import ScoringEngine
    engine = ScoringEngine()
    result = engine.score_sequence("KPSSPPEE")

或命令行:
    pendp score --seq KPSSPPEE
    pendp score curated --seq AKPC  (返回数据库参考分)
"""

import sys
print("⚠️  此脚本已归档，请使用 'pendp score --seq <sequence>' 替代")
sys.exit(1)
