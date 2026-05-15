"""
PENdp 湿实验追踪 — 合成验证行动计划

来源: pendp-peptide-design Skill §四
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timedelta


@dataclass
class WetLabTask:
    id: str
    description: str
    status: str = "pending"  # pending / in_progress / completed / blocked
    timeline: str = ""
    estimated_cost: str = ""
    priority: int = 3  # 1=highest
    notes: str = ""
    completed_date: Optional[str] = None


WETLAB_PLAN: List[WetLabTask] = [
    WetLabTask(
        id="WL-1",
        description="RP-832c 10mg合成 + NHS偶联条件摸索",
        timeline="Week 1-4",
        estimated_cost="中等",
        priority=1,
        notes="首选多肽供应商询价"),
    WetLabTask(
        id="WL-2",
        description="无肽PENdp包载报告mRNA → 静脉注射",
        timeline="Week 1-8",
        estimated_cost="3-5K",
        priority=1,
        notes="低成本验证积雪草酸胞质释放假说"),
    WetLabTask(
        id="WL-3",
        description="RP-832c偶联→M2巨噬细胞摄取实验",
        timeline="Week 5-8",
        priority=1,
        notes="验证靶向效率"),
    WetLabTask(
        id="WL-4",
        description="AA-LNP梯度实验 (0/10/30/50mol% AA)",
        timeline="Week 2-6",
        priority=2,
        notes="确定最佳积雪草酸比例"),
    WetLabTask(
        id="WL-5",
        description="IPF小鼠模型 (TGF-β1诱导)",
        timeline="Week 9-16",
        priority=2,
        notes="体内验证，需CRO或合作实验室"),
    WetLabTask(
        id="WL-6",
        description="AKPC偶联验证",
        timeline="Week 4-8",
        priority=3,
        notes="低成本替代方案，p32靶向"),
    WetLabTask(
        id="WL-7",
        description="数据整理 + ML模型重训练",
        timeline="Week 12-16",
        priority=3,
        notes="湿实验数据反馈到评分模型"),
]


class WetLabTracker:
    """Track wet-lab synthesis and verification progress."""

    def __init__(self):
        self._tasks = {t.id: t for t in WETLAB_PLAN}

    def update_status(self, task_id: str, status: str,
                      notes: str = ""):
        if task_id in self._tasks:
            t = self._tasks[task_id]
            if t.status != "completed" and status == "completed":
                t.completed_date = datetime.now().strftime("%Y-%m-%d")
            t.status = status
            if notes:
                t.notes = notes

    def by_priority(self) -> List[WetLabTask]:
        return sorted(WETLAB_PLAN, key=lambda t: t.priority)

    def by_status(self, status: str) -> List[WetLabTask]:
        return [t for t in WETLAB_PLAN if t.status == status]

    def summary(self) -> dict:
        return {
            "total": len(WETLAB_PLAN),
            "completed": len([t for t in WETLAB_PLAN if t.status == "completed"]),
            "in_progress": len([t for t in WETLAB_PLAN if t.status == "in_progress"]),
            "pending": len([t for t in WETLAB_PLAN if t.status == "pending"]),
            "completion": f"{sum(1 for t in WETLAB_PLAN if t.status == 'completed')}/{len(WETLAB_PLAN)}",
        }

    def timeline(self) -> List[dict]:
        """Return tasks sorted by timeline."""
        return [
            {"id": t.id, "desc": t.description, "timeline": t.timeline,
             "status": t.status, "notes": t.notes}
            for t in sorted(WETLAB_PLAN, key=lambda t: t.priority)
        ]
