"""Welcome Screen — personalized welcome experience for developers.

Shows personalized dashboard with quick stats, recent activity,
suggested actions, and getting started progress.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class WelcomeData:
    developer_id: str
    display_name: str
    extensions_count: int = 0
    total_installs: int = 0
    recent_activity: list[str] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)
    onboarding_complete: bool = False
    unread_notifications: int = 0


class ExtensionWelcomeService:
    """Generates personalized welcome data."""

    def __init__(self):
        self._data: dict[str, WelcomeData] = {}

    def generate(self, developer_id: str, display_name: str,
                 extensions: int = 0, installs: int = 0,
                 activity: list[str] | None = None,
                 onboarding_done: bool = False,
                 unread: int = 0) -> WelcomeData:
        actions = []
        if not onboarding_done:
            actions.append("Complete getting started guide")
        if extensions == 0:
            actions.append("Create your first extension")
        elif installs < 100:
            actions.append("Optimize your listing for more installs")
        if extensions > 0 and installs >= 100:
            actions.append("Apply for verified developer status")

        data = WelcomeData(
            developer_id=developer_id, display_name=display_name,
            extensions_count=extensions, total_installs=installs,
            recent_activity=activity or [], suggested_actions=actions,
            onboarding_complete=onboarding_done, unread_notifications=unread,
        )
        self._data[developer_id] = data
        return data

    def get_greeting(self, developer_id: str) -> str:
        data = self._data.get(developer_id)
        if not data:
            return "Welcome to OpenSkill Developer Platform!"
        if data.extensions_count == 0:
            return f"Welcome, {data.display_name}! Ready to build your first extension?"
        return f"Welcome back, {data.display_name}! You have {data.extensions_count} extensions with {data.total_installs:,} installs."

    def get_data(self, developer_id: str) -> WelcomeData | None:
        return self._data.get(developer_id)
