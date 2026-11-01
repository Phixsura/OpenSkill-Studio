"""Consumer API Token Scope Audit — audit scope usage across tokens."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class ScopeUsageRecord:
    token_id: str
    consumer_id: str
    scope: str
    endpoint: str
    granted: bool
    timestamp: datetime

@dataclass
class ScopeAuditSummary:
    consumer_id: str
    total_checks: int
    granted_count: int
    denied_count: int
    unique_scopes_used: int
    most_used_scope: str
    most_denied_scope: str

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiTokenScopeAudit:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str], list[ScopeUsageRecord]] = {}

    def record(self, installation_id: str, record: ScopeUsageRecord) -> ScopeUsageRecord:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, record.consumer_id)
        if key not in self._records:
            self._records[key] = []
        self._records[key].append(record)
        if len(self._records[key]) > 50000:
            self._records[key] = self._records[key][-50000:]
        return record

    def get_summary(self, installation_id: str, consumer_id: str) -> ScopeAuditSummary:
        records = self._records.get((installation_id, consumer_id), [])
        if not records:
            return ScopeAuditSummary(consumer_id=consumer_id, total_checks=0, granted_count=0, denied_count=0, unique_scopes_used=0, most_used_scope="", most_denied_scope="")
        granted = [r for r in records if r.granted]
        denied = [r for r in records if not r.granted]
        scope_counts: dict[str, int] = {}
        denied_counts: dict[str, int] = {}
        for r in granted:
            scope_counts[r.scope] = scope_counts.get(r.scope, 0) + 1
        for r in denied:
            denied_counts[r.scope] = denied_counts.get(r.scope, 0) + 1
        most_used = max(scope_counts, key=scope_counts.get) if scope_counts else ""
        most_denied = max(denied_counts, key=denied_counts.get) if denied_counts else ""
        return ScopeAuditSummary(consumer_id=consumer_id, total_checks=len(records), granted_count=len(granted), denied_count=len(denied), unique_scopes_used=len(scope_counts), most_used_scope=most_used, most_denied_scope=most_denied)

    def get_unused_scopes(self, installation_id: str, consumer_id: str, all_scopes: set[str]) -> list[str]:
        records = self._records.get((installation_id, consumer_id), [])
        used = {r.scope for r in records if r.granted}
        return sorted(all_scopes - used)

    def get_denied_log(self, installation_id: str, consumer_id: str, limit: int = 20) -> list[ScopeUsageRecord]:
        records = self._records.get((installation_id, consumer_id), [])
        return list(reversed([r for r in records if not r.granted][-limit:]))
