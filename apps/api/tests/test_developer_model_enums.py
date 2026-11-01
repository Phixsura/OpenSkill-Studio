"""Developer model enum coverage."""

import pytest
from app.models.developer import (
    AppStatus, AppVisibility, AppVersionReviewStatus, InstallationStatus,
    SandboxExecutionStatus, DeveloperStatus, AppCategory, UiSurface,
    RateLimitTier, AutomationActionType,
)

ENUM_CASES = [
    (AppStatus, ["DRAFT", "TESTING", "SUBMITTED", "APPROVED", "PUBLISHED", "DEPRECATED", "REVOKED"]),
    (AppVersionReviewStatus, ["PENDING", "APPROVED", "REJECTED"]),
    (InstallationStatus, ["ACTIVE", "SUSPENDED", "UNINSTALLED"]),
    (SandboxExecutionStatus, ["RUNNING", "COMPLETED", "FAILED", "TIMEOUT", "CANCELLED"]),
    (DeveloperStatus, ["ACTIVE"]),
    (AppCategory, ["connector", "automation", "analytics"]),
    (AppVisibility, ["PRIVATE", "PUBLIC"]),
]

@pytest.mark.parametrize("enum_cls,expected", ENUM_CASES, ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x))
def test_enum_contains(enum_cls, expected):
    names = {m.name for m in enum_cls}
    values = {m.value for m in enum_cls}
    for e in expected:
        assert e in names or e in values, f"{enum_cls.__name__} missing {e}"

def test_ui_surface_count():
    assert len(UiSurface) >= 7

def test_rate_limit_tier_count():
    assert len(RateLimitTier) >= 2

def test_automation_action_type_count():
    assert len(AutomationActionType) >= 3
