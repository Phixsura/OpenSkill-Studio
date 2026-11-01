"""Tests for all developer platform enum definitions."""

from app.models.developer import (
    AppCategory, AppStatus, AppVisibility, AppVersionReviewStatus,
    AutomationActionType, DeveloperStatus, InstallationStatus,
    RateLimitTier, SandboxExecutionStatus, UiSurface,
)
from app.models.webhook_delivery import DeliveryStatus


def test_developer_status_values():
    assert set(s.value for s in DeveloperStatus) == {"active", "suspended", "revoked"}

def test_app_category_values():
    assert len(AppCategory) == 7

def test_app_visibility_values():
    assert set(v.value for v in AppVisibility) == {"private", "unlisted", "public"}

def test_app_status_values():
    assert len(AppStatus) == 7
    assert "draft" in [s.value for s in AppStatus]
    assert "revoked" in [s.value for s in AppStatus]

def test_review_status_values():
    assert set(s.value for s in AppVersionReviewStatus) == {"pending", "approved", "rejected", "revoked"}

def test_installation_status_values():
    assert set(s.value for s in InstallationStatus) == {"active", "suspended", "uninstalled"}

def test_rate_limit_tier_values():
    assert set(t.value for t in RateLimitTier) == {"standard", "elevated", "unlimited"}

def test_automation_action_type_values():
    assert set(a.value for a in AutomationActionType) == {"webhook", "sandbox_function", "api_call", "notification"}

def test_sandbox_execution_status_values():
    assert set(s.value for s in SandboxExecutionStatus) == {"running", "completed", "failed", "timeout", "cancelled"}

def test_ui_surface_values():
    assert len(UiSurface) == 8
    assert "dashboard_card" in [s.value for s in UiSurface]

def test_delivery_status_values():
    assert set(s.value for s in DeliveryStatus) == {"pending", "delivered", "failed", "retrying"}

def test_all_enums_are_str_enum():
    for enum_cls in [DeveloperStatus, AppCategory, AppVisibility, AppStatus,
                     AppVersionReviewStatus, InstallationStatus, RateLimitTier,
                     AutomationActionType, SandboxExecutionStatus, UiSurface, DeliveryStatus]:
        for member in enum_cls:
            assert isinstance(member.value, str), f"{enum_cls.__name__}.{member.name} is not str"

def test_app_status_lifecycle_states():
    states = [s.value for s in AppStatus]
    lifecycle = ["draft", "testing", "submitted", "approved", "published", "deprecated", "revoked"]
    for state in lifecycle:
        assert state in states, f"Missing lifecycle state: {state}"

def test_ui_surfaces_count():
    surfaces = [s.value for s in UiSurface]
    expected = ["dashboard_card", "project_sidebar", "cohort_tool", "submission_panel",
                "registry_detail", "settings_page", "client_portal_widget", "operator_console"]
    for s in expected:
        assert s in surfaces

def test_categories_count():
    cats = [c.value for c in AppCategory]
    expected = ["connector", "workflow_adapter", "ui_extension", "analytics",
                "automation", "content_pack", "ecosystem_source"]
    for cat in expected:
        assert cat in cats
