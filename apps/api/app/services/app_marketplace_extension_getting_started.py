"""Getting Started — interactive checklist for new extension developers.

Tracks onboarding progress, prerequisites, and provides contextual
help links for each step of the developer journey.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ChecklistItem:
    item_id: str
    title: str
    description: str
    help_url: str = ""
    completed: bool = False
    order: int = 0


STARTER_CHECKLIST = [
    ("account", "Create Developer Account", "Sign up for a developer account", "/docs/signup", 1),
    ("install_cli", "Install CLI Tools", "Install the OpenSkill CLI", "/docs/cli", 2),
    ("scaffold", "Scaffold Extension", "Create your first extension project", "/docs/scaffold", 3),
    ("manifest", "Configure Manifest", "Set up manifest.json with metadata", "/docs/manifest", 4),
    ("local_dev", "Run Locally", "Start local development server", "/docs/local-dev", 5),
    ("write_tests", "Write Tests", "Add tests for your extension", "/docs/testing", 6),
    ("submit", "Submit for Review", "Submit to the marketplace", "/docs/submit", 7),
    ("publish", "Publish", "Publish your extension", "/docs/publish", 8),
]


class ExtensionGettingStartedService:
    """Interactive onboarding checklist for developers."""

    def __init__(self):
        self._checklists: dict[str, list[ChecklistItem]] = {}

    def initialize(self, developer_id: str) -> list[ChecklistItem]:
        items = [ChecklistItem(
            item_id=iid, title=title, description=desc,
            help_url=url, order=order,
        ) for iid, title, desc, url, order in STARTER_CHECKLIST]
        self._checklists[developer_id] = items
        return items

    def complete_item(self, developer_id: str, item_id: str) -> bool:
        items = self._checklists.get(developer_id, [])
        for item in items:
            if item.item_id == item_id:
                item.completed = True
                return True
        return False

    def get_progress(self, developer_id: str) -> dict:
        items = self._checklists.get(developer_id, [])
        if not items:
            return {"initialized": False}
        completed = sum(1 for i in items if i.completed)
        total = len(items)
        next_item = next((i for i in sorted(items, key=lambda x: x.order) if not i.completed), None)
        return {
            "initialized": True,
            "completed": completed,
            "total": total,
            "percent": round(completed / total * 100),
            "next_step": next_item.title if next_item else None,
            "next_help": next_item.help_url if next_item else None,
            "all_done": completed == total,
        }

    def get_checklist(self, developer_id: str) -> list[ChecklistItem]:
        return sorted(self._checklists.get(developer_id, []), key=lambda i: i.order)
