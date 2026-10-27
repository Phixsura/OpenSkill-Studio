"""Extension Release Manager — manage release lifecycle with approval gates."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class Release:
    release_id: str
    extension_id: str
    version: str
    changelog: list[str] = field(default_factory=list)
    status: str = "draft"  # draft, pending_review, approved, published, rejected
    reviewer_id: str = ""
    review_comment: str = ""
    created_at: float = 0.0
    published_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class ExtReleaseMgrService:
    def __init__(self):
        self._releases: dict[str, Release] = {}
        self._counter = 0

    def create_draft(self, extension_id: str, version: str,
                     changelog: list[str]) -> Release:
        self._counter += 1
        r = Release(release_id=f"rel-{self._counter}", extension_id=extension_id,
                    version=version, changelog=changelog)
        self._releases[r.release_id] = r
        return r

    def submit_for_review(self, release_id: str) -> bool:
        r = self._releases.get(release_id)
        if not r or r.status != "draft": return False
        if not r.changelog:
            return False  # changelog required
        r.status = "pending_review"
        return True

    def approve(self, release_id: str, reviewer_id: str, comment: str = "") -> bool:
        r = self._releases.get(release_id)
        if not r or r.status != "pending_review": return False
        r.status = "approved"
        r.reviewer_id = reviewer_id
        r.review_comment = comment
        return True

    def reject(self, release_id: str, reviewer_id: str, comment: str) -> bool:
        r = self._releases.get(release_id)
        if not r or r.status != "pending_review": return False
        r.status = "rejected"
        r.reviewer_id = reviewer_id
        r.review_comment = comment
        return True

    def publish(self, release_id: str) -> bool:
        r = self._releases.get(release_id)
        if not r or r.status != "approved": return False
        r.status = "published"
        r.published_at = time.time()
        return True

    def get_latest(self, extension_id: str) -> Release | None:
        published = [r for r in self._releases.values()
                     if r.extension_id == extension_id and r.status == "published"]
        return max(published, key=lambda r: r.published_at) if published else None
