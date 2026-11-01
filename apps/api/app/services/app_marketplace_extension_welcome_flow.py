"""Extension Welcome Flow — onboarding flow for new marketplace users."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class WelcomeStep:
    step_id: str
    title: str
    content: str
    action_label: str = ""
    completed: bool = False


class ExtWelcomeFlowService:
    DEFAULT_STEPS = [
        ("explore", "Explore the Marketplace", "Browse extensions by category or search", "Browse"),
        ("install", "Install Your First Extension", "Find and install an extension that fits your needs", "Browse Extensions"),
        ("api_key", "Get Your API Key", "Generate an API key to access the platform API", "Generate Key"),
        ("docs", "Read the Documentation", "Learn how to build and publish extensions", "Read Docs"),
        ("community", "Join the Community", "Connect with other developers", "Join"),
    ]

    def __init__(self):
        self._flows: dict[str, list[WelcomeStep]] = {}

    def start(self, user_id: str) -> list[WelcomeStep]:
        steps = [WelcomeStep(step_id=sid, title=t, content=c, action_label=a)
                 for sid, t, c, a in self.DEFAULT_STEPS]
        self._flows[user_id] = steps
        return steps

    def complete_step(self, user_id: str, step_id: str) -> bool:
        steps = self._flows.get(user_id, [])
        for s in steps:
            if s.step_id == step_id and not s.completed:
                s.completed = True
                return True
        return False

    def get_progress(self, user_id: str) -> dict:
        steps = self._flows.get(user_id, [])
        done = sum(1 for s in steps if s.completed)
        total = len(steps)
        return {"completed": done, "total": total,
                "percentage": round(done / total * 100) if total else 0,
                "all_done": done == total}

    def skip(self, user_id: str) -> None:
        for s in self._flows.get(user_id, []):
            s.completed = True
