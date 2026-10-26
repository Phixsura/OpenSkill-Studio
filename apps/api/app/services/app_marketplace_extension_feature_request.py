"""Feature Request — collect, vote on, and track feature requests for extensions.

Allows users to submit feature ideas, vote on existing requests,
and developers to track demand and prioritize their roadmap.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class RequestStatus(str, Enum):
    OPEN = "open"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DECLINED = "declined"


@dataclass
class FeatureRequest:
    request_id: str
    extension_id: str
    title: str
    description: str
    author_id: str
    status: RequestStatus = RequestStatus.OPEN
    votes: int = 0
    voters: set[str] = field(default_factory=set)
    created_at: str = ""
    developer_response: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class FeatureRequestService:
    """Manages feature requests with voting and status tracking."""

    def __init__(self):
        self._requests: dict[str, FeatureRequest] = {}

    def submit(self, request_id: str, extension_id: str, title: str,
               description: str, author_id: str) -> FeatureRequest:
        fr = FeatureRequest(request_id, extension_id, title, description, author_id)
        fr.voters.add(author_id)
        fr.votes = 1
        self._requests[request_id] = fr
        return fr

    def vote(self, request_id: str, user_id: str) -> tuple[bool, str]:
        fr = self._requests.get(request_id)
        if not fr:
            return False, "Request not found"
        if user_id in fr.voters:
            return False, "Already voted"
        fr.voters.add(user_id)
        fr.votes += 1
        return True, "Vote recorded"

    def unvote(self, request_id: str, user_id: str) -> bool:
        fr = self._requests.get(request_id)
        if fr and user_id in fr.voters and user_id != fr.author_id:
            fr.voters.discard(user_id)
            fr.votes -= 1
            return True
        return False

    def update_status(self, request_id: str, status: RequestStatus,
                      response: str = "") -> bool:
        fr = self._requests.get(request_id)
        if fr:
            fr.status = status
            if response:
                fr.developer_response = response
            return True
        return False

    def get_requests(self, extension_id: str, status: RequestStatus | None = None,
                     sort_by: str = "votes") -> list[FeatureRequest]:
        reqs = [r for r in self._requests.values() if r.extension_id == extension_id]
        if status:
            reqs = [r for r in reqs if r.status == status]
        if sort_by == "votes":
            reqs.sort(key=lambda r: r.votes, reverse=True)
        elif sort_by == "newest":
            reqs.sort(key=lambda r: r.created_at, reverse=True)
        return reqs

    def get_stats(self, extension_id: str) -> dict:
        reqs = [r for r in self._requests.values() if r.extension_id == extension_id]
        by_status = {s.value: 0 for s in RequestStatus}
        for r in reqs:
            by_status[r.status.value] += 1
        return {
            "extension_id": extension_id,
            "total": len(reqs),
            "total_votes": sum(r.votes for r in reqs),
            "by_status": by_status,
        }
