"""Feature Announcer — highlight new platform features to developers."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class FeatureAnnouncement:
    feature_id: str
    title: str
    description: str
    category: str
    icon: str = "✨"
    dismissed_by: set[str] = field(default_factory=set)
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class FeatureAnnouncerService:
    def __init__(self):
        self._features: list[FeatureAnnouncement] = []

    def announce(self, feature_id: str, title: str, description: str,
                 category: str, icon: str = "✨") -> FeatureAnnouncement:
        fa = FeatureAnnouncement(feature_id=feature_id, title=title,
                                 description=description, category=category, icon=icon)
        self._features.append(fa)
        return fa

    def get_new(self, user_id: str) -> list[FeatureAnnouncement]:
        return [f for f in self._features if user_id not in f.dismissed_by]

    def dismiss(self, user_id: str, feature_id: str) -> bool:
        for f in self._features:
            if f.feature_id == feature_id:
                f.dismissed_by.add(user_id)
                return True
        return False

    def get_all(self) -> list[FeatureAnnouncement]:
        return list(self._features)
