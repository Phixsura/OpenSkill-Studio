"""App Review Scorer — automated quality scoring for marketplace app review.

Computes a composite quality score for apps submitted for marketplace review:
- Code quality signals: manifest completeness, description quality
- Security posture: permission count, critical permission usage
- Metadata: icon, screenshots, privacy policy, support email
- Versioning: changelog, semver compliance
- Publisher trust: developer account age, prior app count
- Weighted composite score (0-100)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class ScoreGrade(str, Enum):
    EXCELLENT = "excellent"   # 90-100
    GOOD = "good"             # 70-89
    FAIR = "fair"             # 50-69
    POOR = "poor"             # 0-49


@dataclass
class ReviewInput:
    """Input data for scoring an app."""

    app_id: str
    name: str
    description: str
    icon_url: str | None
    screenshot_count: int
    privacy_policy_url: str | None
    support_email: str | None
    version: str
    changelog: str | None
    permissions: list[str]
    critical_permissions: list[str]   # subset of permissions that are critical
    manifest_fields_total: int
    manifest_fields_filled: int
    developer_account_age_days: int
    developer_prior_apps: int
    has_tests: bool
    has_documentation: bool


@dataclass
class ScoreBreakdown:
    """Individual score components."""

    name: str
    score: float       # 0-100
    weight: float      # 0-1
    details: str


@dataclass
class ReviewScore:
    """Complete review score result."""

    app_id: str
    composite_score: float     # 0-100 weighted
    grade: ScoreGrade
    breakdown: list[ScoreBreakdown]
    auto_approve: bool         # score >= 80 and no critical issues
    flags: list[str]           # issues requiring human review


def compute_review_score(inp: ReviewInput) -> ReviewScore:
    """Compute a composite quality score for an app."""
    breakdown: list[ScoreBreakdown] = []
    flags: list[str] = []

    # 1. Description quality (weight: 0.15)
    desc_len = len(inp.description)
    if desc_len >= 200:
        desc_score = 100
    elif desc_len >= 100:
        desc_score = 70
    elif desc_len >= 30:
        desc_score = 40
    else:
        desc_score = 10
        flags.append("Description too short")
    breakdown.append(ScoreBreakdown("Description", desc_score, 0.15,
                                     f"{desc_len} chars"))

    # 2. Metadata completeness (weight: 0.15)
    meta_points = 0
    meta_total = 4
    if inp.icon_url:
        meta_points += 1
    else:
        flags.append("Missing app icon")
    if inp.screenshot_count >= 1:
        meta_points += 1
    if inp.privacy_policy_url:
        meta_points += 1
    else:
        flags.append("Missing privacy policy")
    if inp.support_email:
        meta_points += 1
    meta_score = (meta_points / meta_total) * 100
    breakdown.append(ScoreBreakdown("Metadata", meta_score, 0.15,
                                     f"{meta_points}/{meta_total} fields"))

    # 3. Manifest completeness (weight: 0.10)
    if inp.manifest_fields_total > 0:
        manifest_score = (inp.manifest_fields_filled / inp.manifest_fields_total) * 100
    else:
        manifest_score = 50
    breakdown.append(ScoreBreakdown("Manifest", round(manifest_score, 1), 0.10,
                                     f"{inp.manifest_fields_filled}/{inp.manifest_fields_total}"))

    # 4. Security posture (weight: 0.25)
    perm_count = len(inp.permissions)
    critical_count = len(inp.critical_permissions)
    if critical_count == 0 and perm_count <= 5:
        sec_score = 100
    elif critical_count == 0 and perm_count <= 10:
        sec_score = 80
    elif critical_count <= 1:
        sec_score = 50
        flags.append(f"Uses {critical_count} critical permission(s)")
    else:
        sec_score = 20
        flags.append(f"Uses {critical_count} critical permissions — requires security review")
    breakdown.append(ScoreBreakdown("Security", sec_score, 0.25,
                                     f"{perm_count} perms, {critical_count} critical"))

    # 5. Versioning (weight: 0.10)
    ver_score = 50
    if _is_semver(inp.version):
        ver_score += 25
    if inp.changelog and len(inp.changelog) >= 20:
        ver_score += 25
    else:
        flags.append("Missing or short changelog")
    breakdown.append(ScoreBreakdown("Versioning", min(ver_score, 100), 0.10,
                                     f"v{inp.version}"))

    # 6. Publisher trust (weight: 0.15)
    trust_score = 0
    if inp.developer_account_age_days >= 90:
        trust_score += 50
    elif inp.developer_account_age_days >= 30:
        trust_score += 30
    else:
        trust_score += 10
        flags.append("New developer account (< 30 days)")
    if inp.developer_prior_apps >= 3:
        trust_score += 50
    elif inp.developer_prior_apps >= 1:
        trust_score += 30
    else:
        trust_score += 10
    breakdown.append(ScoreBreakdown("Publisher Trust", min(trust_score, 100), 0.15,
                                     f"{inp.developer_account_age_days}d, {inp.developer_prior_apps} apps"))

    # 7. Quality signals (weight: 0.10)
    qual_score = 0
    if inp.has_tests:
        qual_score += 50
    if inp.has_documentation:
        qual_score += 50
    breakdown.append(ScoreBreakdown("Quality", qual_score, 0.10,
                                     f"tests={'✓' if inp.has_tests else '✗'}, docs={'✓' if inp.has_documentation else '✗'}"))

    # Composite
    composite = sum(b.score * b.weight for b in breakdown)
    composite = round(min(100, max(0, composite)), 1)

    if composite >= 90:
        grade = ScoreGrade.EXCELLENT
    elif composite >= 70:
        grade = ScoreGrade.GOOD
    elif composite >= 50:
        grade = ScoreGrade.FAIR
    else:
        grade = ScoreGrade.POOR

    auto_approve = composite >= 80 and not any("critical" in f.lower() for f in flags)

    return ReviewScore(
        app_id=inp.app_id,
        composite_score=composite,
        grade=grade,
        breakdown=breakdown,
        auto_approve=auto_approve,
        flags=flags,
    )


def _is_semver(version: str) -> bool:
    import re
    return bool(re.match(r"^\d+\.\d+\.\d+$", version))
