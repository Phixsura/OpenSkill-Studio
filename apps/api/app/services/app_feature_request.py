"""App Feature Request — collect and prioritize feature requests.

Manages feature requests:
- Submit requests with title and description
- Vote/upvote mechanism
- Status tracking (open/planned/in_progress/done/declined)
- Per-installation scoped requests
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class RequestStatus(str, Enum):
    OPEN = "open"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    DECLINED = "declined"


@dataclass
class FeatureRequest:
    """A feature request."""

    request_id: str
    title: str
    description: str
    submitter: str
    status: RequestStatus = RequestStatus.OPEN
    votes: set[str] = field(default_factory=set)
    tags: list[str] = field(default_factory=list)

    @property
    def vote_count(self) -> int:
        return len(self.votes)


class AppFeatureRequest:
    """Collect and prioritize feature requests."""

    def __init__(self) -> None:
        self._requests: dict[tuple[str, str], FeatureRequest] = {}

    def submit(
        self, installation_id: str, request_id: str, title: str,
        description: str, submitter: str, tags: list[str] | None = None,
    ) -> FeatureRequest:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not title:
            raise ValueError("title is required")

        req = FeatureRequest(
            request_id=request_id, title=title, description=description,
            submitter=submitter, tags=tags or [],
        )
        req.votes.add(submitter)  # auto-upvote by submitter
        self._requests[(installation_id, request_id)] = req
        return req

    def vote(self, installation_id: str, request_id: str, user_id: str) -> FeatureRequest:
        req = self._get(installation_id, request_id)
        req.votes.add(user_id)
        return req

    def update_status(self, installation_id: str, request_id: str, status: RequestStatus) -> FeatureRequest:
        req = self._get(installation_id, request_id)
        req.status = status
        return req

    def top_voted(self, installation_id: str, limit: int = 10) -> list[FeatureRequest]:
        reqs = [r for (inst, _), r in self._requests.items() if inst == installation_id]
        return sorted(reqs, key=lambda r: r.vote_count, reverse=True)[:limit]

    def by_status(self, installation_id: str, status: RequestStatus) -> list[FeatureRequest]:
        return [r for (inst, _), r in self._requests.items() if inst == installation_id and r.status == status]

    def list_all(self, installation_id: str) -> list[FeatureRequest]:
        return [r for (inst, _), r in self._requests.items() if inst == installation_id]

    def _get(self, installation_id: str, request_id: str) -> FeatureRequest:
        key = (installation_id, request_id)
        r = self._requests.get(key)
        if r is None:
            raise KeyError(f"Request {request_id} not found")
        return r
