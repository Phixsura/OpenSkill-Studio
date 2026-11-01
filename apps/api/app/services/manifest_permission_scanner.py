"""Manifest Permission Scanner — static analysis of app manifest permission requests.

Analyzes a developer app's capability manifest to:
- Classify permission scopes by risk level (low/medium/high/critical)
- Detect overly broad permission requests
- Identify unused permissions (requested but never exercised)
- Generate human-readable permission summaries for marketplace display
- Compute a trust score based on permission minimality
- Flag permissions that require additional review
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ── Permission catalog ───────────────────────────────────

PERMISSION_CATALOG: dict[str, dict] = {
    # Read-only scopes (low risk)
    "read:skills": {"risk": RiskLevel.LOW, "category": "content", "description": "View skills and categories"},
    "read:projects": {"risk": RiskLevel.LOW, "category": "content", "description": "View projects and templates"},
    "read:packs": {"risk": RiskLevel.LOW, "category": "content", "description": "View skill/workflow packs"},
    "read:profile": {"risk": RiskLevel.LOW, "category": "identity", "description": "View user display name and avatar"},
    "read:cohorts": {"risk": RiskLevel.LOW, "category": "content", "description": "View cohort information"},
    "read:certificates": {"risk": RiskLevel.LOW, "category": "content", "description": "View issued certificates"},
    "read:portfolio": {"risk": RiskLevel.LOW, "category": "content", "description": "View public portfolio items"},
    "read:notifications": {"risk": RiskLevel.LOW, "category": "system", "description": "View notifications"},
    # Write scopes (medium risk)
    "write:skills": {"risk": RiskLevel.MEDIUM, "category": "content", "description": "Create and update skills"},
    "write:projects": {"risk": RiskLevel.MEDIUM, "category": "content", "description": "Create and update projects"},
    "write:submissions": {"risk": RiskLevel.MEDIUM, "category": "content", "description": "Create and grade submissions"},
    "write:evaluations": {"risk": RiskLevel.MEDIUM, "category": "content", "description": "Trigger AI evaluations"},
    "write:cohorts": {"risk": RiskLevel.MEDIUM, "category": "content", "description": "Manage cohort membership"},
    "write:notifications": {"risk": RiskLevel.MEDIUM, "category": "system", "description": "Send notifications"},
    "write:webhooks": {"risk": RiskLevel.MEDIUM, "category": "system", "description": "Manage webhook subscriptions"},
    # Sensitive scopes (high risk)
    "read:email": {"risk": RiskLevel.HIGH, "category": "identity", "description": "View user email address"},
    "read:org_members": {"risk": RiskLevel.HIGH, "category": "identity", "description": "List organization members"},
    "write:org_settings": {"risk": RiskLevel.HIGH, "category": "admin", "description": "Modify organization settings"},
    "write:packs": {"risk": RiskLevel.HIGH, "category": "content", "description": "Publish and modify packs"},
    "write:certificates": {"risk": RiskLevel.HIGH, "category": "content", "description": "Issue certificates"},
    "execute:sandbox": {"risk": RiskLevel.HIGH, "category": "runtime", "description": "Run code in sandbox"},
    "read:analytics": {"risk": RiskLevel.HIGH, "category": "analytics", "description": "Access usage analytics"},
    # Critical scopes (requires additional review)
    "admin:org": {"risk": RiskLevel.CRITICAL, "category": "admin", "description": "Full organization admin access"},
    "write:users": {"risk": RiskLevel.CRITICAL, "category": "identity", "description": "Modify user accounts"},
    "write:billing": {"risk": RiskLevel.CRITICAL, "category": "billing", "description": "Manage billing and subscriptions"},
    "delete:data": {"risk": RiskLevel.CRITICAL, "category": "data", "description": "Permanently delete data"},
    "read:secrets": {"risk": RiskLevel.CRITICAL, "category": "security", "description": "Access stored secrets"},
    "impersonate:user": {"risk": RiskLevel.CRITICAL, "category": "security", "description": "Act on behalf of users"},
}


@dataclass
class PermissionAnalysis:
    """Result of analyzing a single permission scope."""

    scope: str
    risk: RiskLevel
    category: str
    description: str
    known: bool  # whether this scope is in the catalog
    requires_review: bool = False


@dataclass
class ManifestScanResult:
    """Complete scan result for a manifest's permission requests."""

    permissions: list[PermissionAnalysis]
    total_scopes: int
    risk_summary: dict[str, int]  # risk level → count
    trust_score: float  # 0-100, higher = more trustworthy
    categories: dict[str, list[str]]  # category → scopes
    warnings: list[str]
    requires_human_review: bool
    review_reasons: list[str]
    human_summary: str  # one-paragraph for marketplace display


@dataclass
class OverprivilegeReport:
    """Report on permissions requested but never used."""

    requested: set[str]
    exercised: set[str]
    unused: set[str]
    unused_pct: float
    recommendation: str


def scan_permissions(requested: list[str]) -> ManifestScanResult:
    """Analyze a list of requested permission scopes.

    Returns a ManifestScanResult with risk classification,
    trust score, and human-readable summary.
    """
    permissions: list[PermissionAnalysis] = []
    risk_counts: dict[str, int] = {r.value: 0 for r in RiskLevel}
    categories: dict[str, list[str]] = {}
    warnings: list[str] = []
    review_reasons: list[str] = []

    for scope in requested:
        catalog_entry = PERMISSION_CATALOG.get(scope)
        if catalog_entry:
            risk = catalog_entry["risk"]
            category = catalog_entry["category"]
            description = catalog_entry["description"]
            known = True
        else:
            risk = RiskLevel.HIGH  # unknown scopes are treated as high risk
            category = "unknown"
            description = f"Unknown permission: {scope}"
            known = False
            warnings.append(f"Unknown permission scope '{scope}' — treated as high risk")

        requires_review = risk in (RiskLevel.HIGH, RiskLevel.CRITICAL)
        if risk == RiskLevel.CRITICAL:
            review_reasons.append(f"Critical permission requested: {scope}")

        permissions.append(PermissionAnalysis(
            scope=scope,
            risk=risk,
            category=category,
            description=description,
            known=known,
            requires_review=requires_review,
        ))
        risk_counts[risk.value] = risk_counts.get(risk.value, 0) + 1
        categories.setdefault(category, []).append(scope)

    # Broad permission warnings
    if len(requested) > 15:
        warnings.append(f"App requests {len(requested)} permissions — consider minimizing")
    if "admin:org" in requested and "delete:data" in requested:
        warnings.append("App requests both admin and delete access — review carefully")
    if "impersonate:user" in requested:
        warnings.append("App requests user impersonation — requires security review")

    # Trust score: 100 = no permissions, lower for riskier scopes
    trust_score = _compute_trust_score(risk_counts, len(requested))

    # Human summary
    human_summary = _build_summary(permissions, categories)

    requires_human_review = bool(review_reasons) or risk_counts.get("critical", 0) > 0

    return ManifestScanResult(
        permissions=permissions,
        total_scopes=len(requested),
        risk_summary=risk_counts,
        trust_score=round(trust_score, 1),
        categories=categories,
        warnings=warnings,
        requires_human_review=requires_human_review,
        review_reasons=review_reasons,
        human_summary=human_summary,
    )


def detect_overprivilege(requested: list[str], exercised: list[str]) -> OverprivilegeReport:
    """Compare requested permissions with actually exercised ones.

    Used to detect apps that request more permissions than they use.
    """
    req_set = set(requested)
    ex_set = set(exercised)
    unused = req_set - ex_set
    unused_pct = (len(unused) / len(req_set) * 100) if req_set else 0.0

    if unused_pct > 50:
        recommendation = "Consider removing unused permissions to improve trust score"
    elif unused_pct > 25:
        recommendation = "Some requested permissions are not being used"
    elif unused:
        recommendation = "Minor: a few permissions are not yet exercised"
    else:
        recommendation = "All requested permissions are being used — good practice"

    return OverprivilegeReport(
        requested=req_set,
        exercised=ex_set,
        unused=unused,
        unused_pct=round(unused_pct, 1),
        recommendation=recommendation,
    )


# ── Internal helpers ─────────────────────────────────────

RISK_WEIGHTS = {
    RiskLevel.LOW.value: 2,
    RiskLevel.MEDIUM.value: 5,
    RiskLevel.HIGH.value: 15,
    RiskLevel.CRITICAL.value: 30,
}


def _compute_trust_score(risk_counts: dict[str, int], total: int) -> float:
    """Compute a 0-100 trust score. 100 = no permissions, decreases with risk."""
    if total == 0:
        return 100.0

    penalty = sum(
        risk_counts.get(level, 0) * weight
        for level, weight in RISK_WEIGHTS.items()
    )
    # Scale: each point of penalty reduces score from 100
    score = max(0.0, 100.0 - penalty)
    return score


def _build_summary(permissions: list[PermissionAnalysis],
                   categories: dict[str, list[str]]) -> str:
    """Generate a human-readable permission summary for marketplace display."""
    if not permissions:
        return "This app does not request any special permissions."

    parts = []
    cat_labels = {
        "content": "content",
        "identity": "identity information",
        "admin": "admin settings",
        "system": "system features",
        "runtime": "code execution",
        "analytics": "analytics data",
        "billing": "billing",
        "data": "data management",
        "security": "security features",
    }

    for cat, scopes in sorted(categories.items()):
        label = cat_labels.get(cat, cat)
        count = len(scopes)
        if count == 1:
            parts.append(f"{label} ({scopes[0]})")
        else:
            parts.append(f"{count} {label} permissions")

    summary = "This app accesses: " + ", ".join(parts) + "."

    critical_count = sum(1 for p in permissions if p.risk == RiskLevel.CRITICAL)
    if critical_count:
        summary += f" ⚠️ Includes {critical_count} critical-level permission(s) requiring review."

    return summary
