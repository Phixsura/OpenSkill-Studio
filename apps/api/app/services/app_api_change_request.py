"""App API Change Request — manage API change proposals.

Manages change requests:
- Submit change proposals with impact assessment
- Approval workflow
- Track implementation status
- Per-installation scoped requests
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class ChangeStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


@dataclass
class ChangeRequest:
    """An API change request."""

    request_id: str
    title: str
    description: str
    impact: str  # "none", "minor", "major", "breaking"
    status: ChangeStatus = ChangeStatus.DRAFT
    submitter: str = ""
    reviewer: str = ""


VALID_IMPACTS = {"none", "minor", "major", "breaking"}


class AppAPIChangeRequest:
    """Manage API change proposals."""

    def __init__(self) -> None:
        self._requests: dict[tuple[str, str], ChangeRequest] = {}

    def submit(
        self, installation_id: str, request_id: str, title: str,
        description: str, impact: str, submitter: str,
    ) -> ChangeRequest:
        if not installation_id:
            raise ValueError("installation_id is required")
        if impact not in VALID_IMPACTS:
            raise ValueError(f"impact must be one of {VALID_IMPACTS}")

        key = (installation_id, request_id)
        if key in self._requests:
            raise ValueError(f"Request {request_id} already exists")

        cr = ChangeRequest(
            request_id=request_id, title=title, description=description,
            impact=impact, status=ChangeStatus.PENDING, submitter=submitter,
        )
        self._requests[key] = cr
        return cr

    def approve(self, installation_id: str, request_id: str, reviewer: str) -> ChangeRequest:
        cr = self._get(installation_id, request_id)
        if cr.status != ChangeStatus.PENDING:
            raise ValueError("Can only approve pending requests")
        cr.status = ChangeStatus.APPROVED
        cr.reviewer = reviewer
        return cr

    def reject(self, installation_id: str, request_id: str, reviewer: str) -> ChangeRequest:
        cr = self._get(installation_id, request_id)
        cr.status = ChangeStatus.REJECTED
        cr.reviewer = reviewer
        return cr

    def implement(self, installation_id: str, request_id: str) -> ChangeRequest:
        cr = self._get(installation_id, request_id)
        if cr.status != ChangeStatus.APPROVED:
            raise ValueError("Can only implement approved requests")
        cr.status = ChangeStatus.IMPLEMENTED
        return cr

    def pending(self, installation_id: str) -> list[ChangeRequest]:
        return [r for (inst, _), r in self._requests.items() if inst == installation_id and r.status == ChangeStatus.PENDING]

    def list_requests(self, installation_id: str) -> list[ChangeRequest]:
        return [r for (inst, _), r in self._requests.items() if inst == installation_id]

    def _get(self, installation_id: str, request_id: str) -> ChangeRequest:
        key = (installation_id, request_id)
        r = self._requests.get(key)
        if r is None:
            raise KeyError(f"Request {request_id} not found")
        return r
