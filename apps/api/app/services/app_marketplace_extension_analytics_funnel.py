"""Analytics Funnel — track conversion funnels for extension marketplace.

Measures user journey through discovery → view → install → activate → retain
stages with drop-off analysis, cohort segmentation, and funnel comparison.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class FunnelStage(str, Enum):
    DISCOVERY = "discovery"
    VIEW = "view"
    INSTALL = "install"
    ACTIVATE = "activate"
    RETAIN = "retain"


STAGE_ORDER = list(FunnelStage)


@dataclass
class FunnelEvent:
    extension_id: str
    user_id: str
    stage: FunnelStage
    timestamp: float
    source: str = ""  # search, browse, recommendation, direct


@dataclass
class FunnelReport:
    extension_id: str
    stages: dict[str, int]
    conversion_rates: dict[str, float]
    drop_off: dict[str, float]
    total_users: int


class AnalyticsFunnelService:
    """Tracks and analyzes marketplace conversion funnels."""

    def __init__(self):
        self._events: list[FunnelEvent] = []
        self._user_stages: dict[str, dict[str, FunnelStage]] = defaultdict(dict)

    def track(self, extension_id: str, user_id: str, stage: FunnelStage,
              timestamp: float = 0.0, source: str = "") -> FunnelEvent:
        event = FunnelEvent(
            extension_id=extension_id, user_id=user_id,
            stage=stage, timestamp=timestamp, source=source,
        )
        self._events.append(event)
        current = self._user_stages.get(extension_id, {}).get(user_id)
        if current is None or STAGE_ORDER.index(stage) > STAGE_ORDER.index(current):
            self._user_stages.setdefault(extension_id, {})[user_id] = stage
        return event

    def get_funnel(self, extension_id: str) -> FunnelReport:
        user_max = self._user_stages.get(extension_id, {})
        stage_counts: dict[str, int] = {s.value: 0 for s in FunnelStage}
        for user_id, max_stage in user_max.items():
            idx = STAGE_ORDER.index(max_stage)
            for i in range(idx + 1):
                stage_counts[STAGE_ORDER[i].value] += 1

        total = stage_counts.get("discovery", 0) or 1
        conversion: dict[str, float] = {}
        drop_off: dict[str, float] = {}
        for i, stage in enumerate(STAGE_ORDER):
            conversion[stage.value] = round(stage_counts[stage.value] / total * 100, 1)
            if i > 0:
                prev_count = stage_counts[STAGE_ORDER[i - 1].value] or 1
                drop_off[stage.value] = round(
                    (1 - stage_counts[stage.value] / prev_count) * 100, 1
                )

        return FunnelReport(
            extension_id=extension_id, stages=stage_counts,
            conversion_rates=conversion, drop_off=drop_off,
            total_users=len(user_max),
        )

    def get_source_breakdown(self, extension_id: str) -> dict[str, dict[str, int]]:
        by_source: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for e in self._events:
            if e.extension_id == extension_id and e.source:
                by_source[e.source][e.stage.value] += 1
        return {s: dict(stages) for s, stages in by_source.items()}

    def compare_funnels(self, ext_ids: list[str]) -> dict[str, dict]:
        result = {}
        for eid in ext_ids:
            report = self.get_funnel(eid)
            result[eid] = {
                "total_users": report.total_users,
                "install_rate": report.conversion_rates.get("install", 0),
                "retain_rate": report.conversion_rates.get("retain", 0),
            }
        return result
