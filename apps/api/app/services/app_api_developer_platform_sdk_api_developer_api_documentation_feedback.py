"""App API Developer Documentation Feedback — collect feedback on API docs pages."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class DocFeedback:
    feedback_id: str
    page_path: str
    helpful: bool
    comment: str = ""
    developer_id: str = ""
    created_at: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiDeveloperApiDocumentationFeedback:
    def __init__(self) -> None:
        self._feedback: dict[str, list[DocFeedback]] = {}

    def submit(self, installation_id: str, feedback_id: str, page_path: str, helpful: bool, comment: str = "", developer_id: str = "") -> DocFeedback:
        if not installation_id: raise ValueError("installation_id is required")
        f = DocFeedback(feedback_id=feedback_id, page_path=page_path, helpful=helpful, comment=comment, developer_id=developer_id)
        self._feedback.setdefault(installation_id, []).append(f)
        return f

    def helpfulness_rate(self, installation_id: str, page_path: str | None = None) -> float:
        fb = self._feedback.get(installation_id, [])
        if page_path: fb = [f for f in fb if f.page_path == page_path]
        if not fb: return 0.0
        return round(sum(1 for f in fb if f.helpful) / len(fb) * 100, 1)

    def worst_pages(self, installation_id: str, limit: int = 5) -> list[tuple[str, float]]:
        pages: dict[str, list[bool]] = {}
        for f in self._feedback.get(installation_id, []):
            pages.setdefault(f.page_path, []).append(f.helpful)
        scored = [(p, round(sum(h) / len(h) * 100, 1)) for p, h in pages.items() if len(h) >= 3]
        return sorted(scored, key=lambda x: x[1])[:limit]

    def recent_comments(self, installation_id: str, limit: int = 10) -> list[DocFeedback]:
        fb = [f for f in self._feedback.get(installation_id, []) if f.comment]
        return list(reversed(fb[-limit:]))

    def total_feedback(self, installation_id: str) -> int:
        return len(self._feedback.get(installation_id, []))
