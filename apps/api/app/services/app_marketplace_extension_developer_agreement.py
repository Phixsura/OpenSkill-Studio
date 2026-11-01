"""Developer Agreement — manage developer ToS acceptance and compliance.

Tracks agreement versions, developer acceptance history, compliance
requirements, and enforcement actions for marketplace participation.
"""
from __future__ import annotations
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    SUSPENDED = "suspended"


@dataclass
class AgreementVersion:
    version: str
    title: str
    effective_date: str
    content_hash: str
    requires_re_acceptance: bool = False


@dataclass
class DeveloperAcceptance:
    acceptance_id: str
    developer_id: str
    agreement_version: str
    accepted_at: str
    ip_address: str = ""


@dataclass
class ComplianceRecord:
    record_id: str
    developer_id: str
    status: ComplianceStatus
    violations: list[str] = field(default_factory=list)
    warnings_count: int = 0
    last_reviewed: str = ""


class DeveloperAgreementService:
    """Manages developer agreements and compliance tracking."""

    def __init__(self):
        self._versions: dict[str, AgreementVersion] = {}
        self._current_version: str = ""
        self._acceptances: dict[str, list[DeveloperAcceptance]] = {}
        self._compliance: dict[str, ComplianceRecord] = {}

    def publish_version(self, version: str, title: str,
                        content_hash: str,
                        requires_re_acceptance: bool = False) -> AgreementVersion:
        av = AgreementVersion(
            version=version, title=title,
            effective_date=datetime.now(timezone.utc).isoformat(),
            content_hash=content_hash,
            requires_re_acceptance=requires_re_acceptance,
        )
        self._versions[version] = av
        self._current_version = version
        return av

    def accept(self, developer_id: str, version: str | None = None,
               ip_address: str = "") -> DeveloperAcceptance:
        ver = version or self._current_version
        if ver not in self._versions:
            raise ValueError(f"Agreement version {ver} not found")
        acceptance = DeveloperAcceptance(
            acceptance_id=f"acc_{secrets.token_urlsafe(10)}",
            developer_id=developer_id, agreement_version=ver,
            accepted_at=datetime.now(timezone.utc).isoformat(),
            ip_address=ip_address,
        )
        self._acceptances.setdefault(developer_id, []).append(acceptance)
        return acceptance

    def has_accepted_current(self, developer_id: str) -> bool:
        if not self._current_version:
            return True
        acceptances = self._acceptances.get(developer_id, [])
        return any(a.agreement_version == self._current_version for a in acceptances)

    def needs_re_acceptance(self, developer_id: str) -> bool:
        if not self._current_version:
            return False
        current = self._versions.get(self._current_version)
        if not current or not current.requires_re_acceptance:
            return False
        return not self.has_accepted_current(developer_id)

    def record_violation(self, developer_id: str, violation: str) -> ComplianceRecord:
        record = self._compliance.get(developer_id)
        if not record:
            record = ComplianceRecord(
                record_id=f"cr_{secrets.token_urlsafe(8)}",
                developer_id=developer_id,
                status=ComplianceStatus.COMPLIANT,
            )
            self._compliance[developer_id] = record

        record.violations.append(violation)
        record.last_reviewed = datetime.now(timezone.utc).isoformat()

        if len(record.violations) >= 3:
            record.status = ComplianceStatus.SUSPENDED
        elif len(record.violations) >= 1:
            record.status = ComplianceStatus.VIOLATION

        return record

    def issue_warning(self, developer_id: str) -> ComplianceRecord:
        record = self._compliance.get(developer_id)
        if not record:
            record = ComplianceRecord(
                record_id=f"cr_{secrets.token_urlsafe(8)}",
                developer_id=developer_id,
                status=ComplianceStatus.COMPLIANT,
            )
            self._compliance[developer_id] = record
        record.warnings_count += 1
        if record.status == ComplianceStatus.COMPLIANT:
            record.status = ComplianceStatus.WARNING
        return record

    def get_compliance(self, developer_id: str) -> dict:
        record = self._compliance.get(developer_id)
        if not record:
            return {"developer_id": developer_id, "status": "compliant",
                    "violations": 0, "warnings": 0}
        return {
            "developer_id": developer_id, "status": record.status.value,
            "violations": len(record.violations), "warnings": record.warnings_count,
            "is_suspended": record.status == ComplianceStatus.SUSPENDED,
        }
