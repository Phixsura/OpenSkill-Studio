"""Developer Onboarding Checklist — guide new developers through setup steps."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class ChecklistItem:
    item_id: str
    title: str
    description: str
    completed: bool = False
    completed_at: float = 0.0
    required: bool = True
    order: int = 0


class DevOnboardingService:
    DEFAULT_ITEMS = [
        ("profile", "Complete Profile", "Add bio, avatar, and links", True),
        ("api_key", "Generate API Key", "Create your first API key", True),
        ("extension", "Create Extension", "Publish your first extension", True),
        ("docs", "Read Documentation", "Review the developer docs", False),
        ("sandbox", "Try Sandbox", "Run code in the sandbox environment", False),
        ("webhook", "Set Up Webhook", "Configure a webhook endpoint", False),
        ("team", "Invite Team Member", "Add a collaborator", False),
    ]

    def __init__(self):
        self._checklists: dict[str, list[ChecklistItem]] = {}

    def get_or_create(self, user_id: str) -> list[ChecklistItem]:
        if user_id not in self._checklists:
            items = []
            for i, (iid, title, desc, req) in enumerate(self.DEFAULT_ITEMS):
                items.append(ChecklistItem(item_id=iid, title=title,
                                          description=desc, required=req, order=i))
            self._checklists[user_id] = items
        return self._checklists[user_id]

    def complete_item(self, user_id: str, item_id: str) -> bool:
        items = self.get_or_create(user_id)
        for item in items:
            if item.item_id == item_id and not item.completed:
                item.completed = True
                item.completed_at = time.time()
                return True
        return False

    def get_progress(self, user_id: str) -> dict:
        items = self.get_or_create(user_id)
        total = len(items)
        done = sum(1 for i in items if i.completed)
        required = [i for i in items if i.required]
        req_done = sum(1 for i in required if i.completed)
        return {"total": total, "completed": done,
                "percentage": round(done / total * 100) if total else 0,
                "required_complete": req_done == len(required)}

    def is_onboarded(self, user_id: str) -> bool:
        return self.get_progress(user_id)["required_complete"]
