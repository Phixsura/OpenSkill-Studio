"""Consumer API Onboarding Checklist — track consumer onboarding progress."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class ChecklistItem:
    item_id: str
    title: str
    description: str = ""
    completed: bool = False
    completed_at: datetime | None = None
    required: bool = True
    order: int = 0

@dataclass
class OnboardingChecklist:
    consumer_id: str
    items: list[ChecklistItem] = field(default_factory=list)
    started_at: datetime | None = None

@dataclass
class OnboardingProgress:
    consumer_id: str
    total: int
    completed: int
    required_completed: int
    required_total: int
    progress_pct: float
    fully_onboarded: bool

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiOnboardingChecklist:
    def __init__(self) -> None:
        self._checklists: dict[tuple[str, str], OnboardingChecklist] = {}

    def create(self, installation_id: str, consumer_id: str, items: list[ChecklistItem], now: datetime | None = None) -> OnboardingChecklist:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not items:
            raise ValueError("At least one item required")
        items.sort(key=lambda i: i.order)
        checklist = OnboardingChecklist(consumer_id=consumer_id, items=items, started_at=now or datetime.utcnow())
        self._checklists[(installation_id, consumer_id)] = checklist
        return checklist

    def complete_item(self, installation_id: str, consumer_id: str, item_id: str, now: datetime | None = None) -> ChecklistItem:
        checklist = self._checklists.get((installation_id, consumer_id))
        if not checklist:
            raise ValueError("Checklist not found")
        for item in checklist.items:
            if item.item_id == item_id:
                item.completed = True
                item.completed_at = now or datetime.utcnow()
                return item
        raise ValueError(f"Item {item_id} not found")

    def get_progress(self, installation_id: str, consumer_id: str) -> OnboardingProgress:
        checklist = self._checklists.get((installation_id, consumer_id))
        if not checklist:
            return OnboardingProgress(consumer_id=consumer_id, total=0, completed=0, required_completed=0, required_total=0, progress_pct=0, fully_onboarded=False)
        total = len(checklist.items)
        completed = sum(1 for i in checklist.items if i.completed)
        req_total = sum(1 for i in checklist.items if i.required)
        req_completed = sum(1 for i in checklist.items if i.required and i.completed)
        pct = (completed / total * 100) if total > 0 else 0
        return OnboardingProgress(consumer_id=consumer_id, total=total, completed=completed, required_completed=req_completed, required_total=req_total, progress_pct=round(pct, 1), fully_onboarded=req_completed >= req_total)

    def get_checklist(self, installation_id: str, consumer_id: str) -> OnboardingChecklist | None:
        return self._checklists.get((installation_id, consumer_id))
