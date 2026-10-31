"""App API Developer API Onboarding Checklist — guided developer setup."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ChecklistItem:
    item_id: str
    title: str
    description: str
    required: bool = True
    completed: bool = False
    order: int = 0

@dataclass
class OnboardingProgress:
    developer_id: str
    items: list[ChecklistItem] = field(default_factory=list)

    @property
    def completion_pct(self) -> float:
        if not self.items: return 0.0
        return round(sum(1 for i in self.items if i.completed) / len(self.items) * 100, 1)

    @property
    def all_required_done(self) -> bool:
        return all(i.completed for i in self.items if i.required)

class AppAPIDeveloperAPIApiOnboardingChecklist:
    def __init__(self) -> None:
        self._progress: dict[tuple[str, str], OnboardingProgress] = {}
        self._templates: dict[str, list[dict]] = {}

    def set_template(self, installation_id: str, items: list[dict]) -> None:
        if not installation_id: raise ValueError("installation_id is required")
        self._templates[installation_id] = items

    def start(self, installation_id: str, developer_id: str) -> OnboardingProgress:
        template = self._templates.get(installation_id, [])
        items = [ChecklistItem(item_id=i["item_id"], title=i["title"], description=i.get("description", ""), required=i.get("required", True), order=idx) for idx, i in enumerate(template)]
        p = OnboardingProgress(developer_id=developer_id, items=items)
        self._progress[(installation_id, developer_id)] = p
        return p

    def complete_item(self, installation_id: str, developer_id: str, item_id: str) -> OnboardingProgress:
        p = self._get(installation_id, developer_id)
        for item in p.items:
            if item.item_id == item_id:
                item.completed = True
                return p
        raise KeyError(f"Item {item_id} not found")

    def get_progress(self, installation_id: str, developer_id: str) -> OnboardingProgress:
        return self._get(installation_id, developer_id)

    def _get(self, installation_id: str, developer_id: str) -> OnboardingProgress:
        key = (installation_id, developer_id)
        p = self._progress.get(key)
        if p is None: raise KeyError(f"No onboarding for {developer_id}")
        return p
