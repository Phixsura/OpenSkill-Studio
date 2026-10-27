"""Tests for App Review Scorer — scoring, grading, flags, auto-approve."""

import pytest

from app.services.app_review_scorer import (
    ReviewInput,
    ScoreGrade,
    compute_review_score,
)


def _good_input(**overrides) -> ReviewInput:
    defaults = dict(
        app_id="app-1", name="Great App",
        description="A comprehensive application that helps users manage their workflow efficiently with powerful features and integrations. "
                     "Supports multiple teams and custom automation rules.",
        icon_url="https://example.com/icon.png",
        screenshot_count=3,
        privacy_policy_url="https://example.com/privacy",
        support_email="support@example.com",
        version="2.1.0",
        changelog="Added new dashboard widgets, fixed OAuth token refresh bug, improved performance.",
        permissions=["read:skills", "read:projects"],
        critical_permissions=[],
        manifest_fields_total=20,
        manifest_fields_filled=18,
        developer_account_age_days=180,
        developer_prior_apps=5,
        has_tests=True,
        has_documentation=True,
    )
    defaults.update(overrides)
    return ReviewInput(**defaults)


def _poor_input(**overrides) -> ReviewInput:
    defaults = dict(
        app_id="app-2", name="Bad App",
        description="An app.",
        icon_url=None,
        screenshot_count=0,
        privacy_policy_url=None,
        support_email=None,
        version="1",
        changelog=None,
        permissions=["admin:org", "delete:data", "impersonate:user", "write:billing",
                      "read:secrets", "write:users", "read:skills", "write:projects"],
        critical_permissions=["admin:org", "delete:data", "impersonate:user"],
        manifest_fields_total=20,
        manifest_fields_filled=5,
        developer_account_age_days=3,
        developer_prior_apps=0,
        has_tests=False,
        has_documentation=False,
    )
    defaults.update(overrides)
    return ReviewInput(**defaults)


class TestCompositeScore:
    def test_good_app_high_score(self):
        result = compute_review_score(_good_input())
        assert result.composite_score >= 80
        assert result.grade in (ScoreGrade.EXCELLENT, ScoreGrade.GOOD)

    def test_poor_app_low_score(self):
        result = compute_review_score(_poor_input())
        assert result.composite_score < 50
        assert result.grade == ScoreGrade.POOR

    def test_score_range_0_100(self):
        for inp in [_good_input(), _poor_input()]:
            result = compute_review_score(inp)
            assert 0 <= result.composite_score <= 100


class TestGrading:
    def test_excellent(self):
        result = compute_review_score(_good_input())
        # With all good signals, should be excellent or good
        assert result.grade in (ScoreGrade.EXCELLENT, ScoreGrade.GOOD)

    def test_fair(self):
        result = compute_review_score(_good_input(
            permissions=["read:skills", "write:projects", "admin:org"],
            critical_permissions=["admin:org"],
            developer_account_age_days=20,
            developer_prior_apps=0,
            has_tests=False,
        ))
        assert result.grade in (ScoreGrade.FAIR, ScoreGrade.GOOD)


class TestBreakdown:
    def test_has_all_components(self):
        result = compute_review_score(_good_input())
        names = {b.name for b in result.breakdown}
        assert "Description" in names
        assert "Metadata" in names
        assert "Security" in names
        assert "Versioning" in names
        assert "Publisher Trust" in names
        assert "Quality" in names

    def test_weights_sum_to_one(self):
        result = compute_review_score(_good_input())
        total_weight = sum(b.weight for b in result.breakdown)
        assert total_weight == pytest.approx(1.0)

    def test_description_score(self):
        short = compute_review_score(_good_input(description="Hi"))
        long = compute_review_score(_good_input(description="A" * 250))
        short_desc = [b for b in short.breakdown if b.name == "Description"][0]
        long_desc = [b for b in long.breakdown if b.name == "Description"][0]
        assert long_desc.score > short_desc.score


class TestFlags:
    def test_missing_icon_flagged(self):
        result = compute_review_score(_good_input(icon_url=None))
        assert any("icon" in f.lower() for f in result.flags)

    def test_missing_privacy_policy_flagged(self):
        result = compute_review_score(_good_input(privacy_policy_url=None))
        assert any("privacy" in f.lower() for f in result.flags)

    def test_critical_permissions_flagged(self):
        result = compute_review_score(_good_input(
            permissions=["admin:org", "read:skills"],
            critical_permissions=["admin:org"],
        ))
        assert any("critical" in f.lower() for f in result.flags)

    def test_new_developer_flagged(self):
        result = compute_review_score(_good_input(developer_account_age_days=5))
        assert any("new developer" in f.lower() for f in result.flags)

    def test_short_description_flagged(self):
        result = compute_review_score(_good_input(description="Short"))
        assert any("description" in f.lower() for f in result.flags)

    def test_no_flags_for_good_app(self):
        result = compute_review_score(_good_input())
        assert len(result.flags) == 0


class TestAutoApprove:
    def test_auto_approve_good_app(self):
        result = compute_review_score(_good_input())
        assert result.auto_approve is True

    def test_no_auto_approve_low_score(self):
        result = compute_review_score(_poor_input())
        assert result.auto_approve is False

    def test_no_auto_approve_critical_permissions(self):
        result = compute_review_score(_good_input(
            permissions=["admin:org", "read:skills"],
            critical_permissions=["admin:org"],
        ))
        assert result.auto_approve is False


class TestSecurity:
    def test_no_permissions_high_security(self):
        result = compute_review_score(_good_input(permissions=[], critical_permissions=[]))
        sec = [b for b in result.breakdown if b.name == "Security"][0]
        assert sec.score == 100

    def test_many_critical_low_security(self):
        result = compute_review_score(_poor_input())
        sec = [b for b in result.breakdown if b.name == "Security"][0]
        assert sec.score <= 30


class TestVersioning:
    def test_semver_with_changelog(self):
        result = compute_review_score(_good_input())
        ver = [b for b in result.breakdown if b.name == "Versioning"][0]
        assert ver.score == 100

    def test_non_semver_no_changelog(self):
        result = compute_review_score(_good_input(version="v1", changelog=None))
        ver = [b for b in result.breakdown if b.name == "Versioning"][0]
        assert ver.score < 100
