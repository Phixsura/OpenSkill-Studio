"""App Scope Analyzer — analyze actual API scope usage vs declared permissions.

Compares what an app declares vs what it actually uses:
- Track which scopes are exercised at runtime
- Identify over-permissioned apps (declared but unused scopes)
- Identify under-permissioned attempts (used but not declared)
- Compliance score (used/declared ratio)
- Recommendations for scope reduction
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime

import structlog

log = structlog.get_logger()


@dataclass
class ScopeUsageRecord:
    """A record of a scope being exercised."""

    scope: str
    endpoint: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ScopeAnalysis:
    """Complete analysis of scope usage vs declaration."""

    app_id: str
    declared_scopes: set[str]
    exercised_scopes: set[str]
    unused_scopes: set[str]
    undeclared_attempts: set[str]
    compliance_pct: float      # exercised ∩ declared / declared
    over_permissioned: bool
    under_permissioned: bool
    usage_counts: dict[str, int]
    recommendations: list[str]


class AppScopeAnalyzer:
    """Analyze app scope usage patterns."""

    def __init__(self):
        # app_id → declared scopes
        self._declared: dict[str, set[str]] = {}
        # app_id → list of usage records
        self._usage: dict[str, list[ScopeUsageRecord]] = {}
        # app_id → set of denied scope attempts
        self._denied: dict[str, set[str]] = {}

    def declare_scopes(self, app_id: str, scopes: list[str]) -> None:
        """Set the declared scopes for an app (from manifest)."""
        self._declared[app_id] = set(scopes)

    def record_usage(self, app_id: str, scope: str, endpoint: str) -> bool:
        """Record a scope being exercised. Returns False if scope not declared."""
        declared = self._declared.get(app_id, set())
        record = ScopeUsageRecord(scope=scope, endpoint=endpoint)
        self._usage.setdefault(app_id, []).append(record)

        if scope not in declared:
            self._denied.setdefault(app_id, set()).add(scope)
            return False
        return True

    def analyze(self, app_id: str) -> ScopeAnalysis:
        """Analyze scope usage vs declarations."""
        declared = self._declared.get(app_id, set())
        records = self._usage.get(app_id, [])
        exercised = {r.scope for r in records}
        denied = self._denied.get(app_id, set())

        # Only count exercised scopes that are actually declared
        valid_exercised = exercised & declared
        unused = declared - exercised
        undeclared = denied

        compliance = (len(valid_exercised) / len(declared) * 100) if declared else 100.0

        # Usage counts
        counts = Counter(r.scope for r in records)

        # Recommendations
        recs: list[str] = []
        if unused:
            recs.append(f"Remove {len(unused)} unused scope(s): {', '.join(sorted(unused))}")
        if undeclared:
            recs.append(f"Add {len(undeclared)} missing scope(s): {', '.join(sorted(undeclared))}")
        if compliance == 100 and not undeclared:
            recs.append("All scopes are correctly utilized — no changes needed")

        return ScopeAnalysis(
            app_id=app_id,
            declared_scopes=declared,
            exercised_scopes=valid_exercised,
            unused_scopes=unused,
            undeclared_attempts=undeclared,
            compliance_pct=round(compliance, 1),
            over_permissioned=len(unused) > 0,
            under_permissioned=len(undeclared) > 0,
            usage_counts=dict(counts),
            recommendations=recs,
        )

    def get_top_scopes(self, app_id: str, limit: int = 10) -> list[tuple[str, int]]:
        """Get most-used scopes ranked by call count."""
        records = self._usage.get(app_id, [])
        counts = Counter(r.scope for r in records)
        return counts.most_common(limit)

    def get_denied_attempts(self, app_id: str) -> set[str]:
        return self._denied.get(app_id, set())
