"""Tests for Manifest Permission Scanner — risk classification, trust score, overprivilege."""

import pytest

from app.services.manifest_permission_scanner import (
    ManifestScanResult,
    OverprivilegeReport,
    RiskLevel,
    detect_overprivilege,
    scan_permissions,
)


class TestScanPermissions:
    def test_empty_permissions(self):
        result = scan_permissions([])
        assert result.total_scopes == 0
        assert result.trust_score == 100.0
        assert result.requires_human_review is False
        assert "does not request" in result.human_summary

    def test_low_risk_only(self):
        result = scan_permissions(["read:skills", "read:projects"])
        assert result.total_scopes == 2
        assert result.risk_summary["low"] == 2
        assert result.risk_summary["critical"] == 0
        assert result.trust_score > 90
        assert result.requires_human_review is False

    def test_critical_triggers_review(self):
        result = scan_permissions(["read:skills", "admin:org"])
        assert result.requires_human_review is True
        assert any("admin:org" in r for r in result.review_reasons)
        assert result.risk_summary["critical"] == 1

    def test_unknown_scope_treated_as_high(self):
        result = scan_permissions(["read:skills", "custom:magic_power"])
        unknown = [p for p in result.permissions if p.scope == "custom:magic_power"]
        assert len(unknown) == 1
        assert unknown[0].risk == RiskLevel.HIGH
        assert unknown[0].known is False
        assert any("Unknown" in w for w in result.warnings)

    def test_risk_summary_counts(self):
        result = scan_permissions([
            "read:skills",      # low
            "read:projects",    # low
            "write:skills",     # medium
            "read:email",       # high
            "admin:org",        # critical
        ])
        assert result.risk_summary["low"] == 2
        assert result.risk_summary["medium"] == 1
        assert result.risk_summary["high"] == 1
        assert result.risk_summary["critical"] == 1

    def test_categories_grouped(self):
        result = scan_permissions(["read:skills", "write:skills", "read:profile"])
        assert "content" in result.categories
        assert "read:skills" in result.categories["content"]
        assert "write:skills" in result.categories["content"]
        assert "identity" in result.categories
        assert "read:profile" in result.categories["identity"]

    def test_broad_permissions_warning(self):
        # Request many permissions
        scopes = [
            "read:skills", "read:projects", "read:packs", "read:profile",
            "read:cohorts", "read:certificates", "read:portfolio",
            "read:notifications", "write:skills", "write:projects",
            "write:submissions", "write:evaluations", "write:cohorts",
            "write:notifications", "write:webhooks", "read:email",
        ]
        result = scan_permissions(scopes)
        assert any("consider minimizing" in w.lower() for w in result.warnings)

    def test_impersonation_warning(self):
        result = scan_permissions(["impersonate:user"])
        assert any("impersonation" in w.lower() for w in result.warnings)
        assert result.requires_human_review is True

    def test_admin_plus_delete_warning(self):
        result = scan_permissions(["admin:org", "delete:data"])
        assert any("admin and delete" in w.lower() for w in result.warnings)

    def test_trust_score_decreases_with_risk(self):
        low_only = scan_permissions(["read:skills"])
        medium = scan_permissions(["write:skills"])
        high = scan_permissions(["read:email"])
        critical = scan_permissions(["admin:org"])
        assert low_only.trust_score > medium.trust_score
        assert medium.trust_score > high.trust_score
        assert high.trust_score > critical.trust_score

    def test_trust_score_never_negative(self):
        # Request all critical permissions
        result = scan_permissions([
            "admin:org", "write:users", "write:billing",
            "delete:data", "read:secrets", "impersonate:user",
        ])
        assert result.trust_score >= 0

    def test_human_summary_includes_categories(self):
        result = scan_permissions(["read:skills", "read:email", "execute:sandbox"])
        assert "content" in result.human_summary
        assert "identity" in result.human_summary

    def test_human_summary_critical_warning(self):
        result = scan_permissions(["admin:org"])
        assert "⚠️" in result.human_summary
        assert "critical" in result.human_summary.lower()

    def test_permission_descriptions(self):
        result = scan_permissions(["read:skills"])
        assert result.permissions[0].description == "View skills and categories"

    def test_requires_review_flags(self):
        result = scan_permissions(["read:skills", "read:email", "admin:org"])
        review_scopes = [p.scope for p in result.permissions if p.requires_review]
        assert "read:email" in review_scopes
        assert "admin:org" in review_scopes
        assert "read:skills" not in review_scopes


class TestDetectOverprivilege:
    def test_all_used(self):
        report = detect_overprivilege(
            requested=["read:skills", "write:skills"],
            exercised=["read:skills", "write:skills"],
        )
        assert len(report.unused) == 0
        assert report.unused_pct == 0.0
        assert "good practice" in report.recommendation.lower()

    def test_some_unused(self):
        report = detect_overprivilege(
            requested=["read:skills", "write:skills", "read:email"],
            exercised=["read:skills"],
        )
        assert report.unused == {"write:skills", "read:email"}
        assert report.unused_pct == pytest.approx(66.7, abs=0.1)

    def test_minor_unused(self):
        report = detect_overprivilege(
            requested=["read:skills", "write:skills", "read:projects", "read:cohorts"],
            exercised=["read:skills", "write:skills", "read:projects"],
        )
        assert report.unused == {"read:cohorts"}
        assert report.unused_pct == 25.0
        assert "not yet exercised" in report.recommendation.lower()

    def test_empty_requested(self):
        report = detect_overprivilege(requested=[], exercised=[])
        assert report.unused_pct == 0.0

    def test_exercised_not_in_requested_ignored(self):
        # Exercised something not requested (shouldn't happen but handle gracefully)
        report = detect_overprivilege(
            requested=["read:skills"],
            exercised=["read:skills", "write:skills"],
        )
        assert len(report.unused) == 0
