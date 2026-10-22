"""Parametrized tests for all enum values are str type."""

import pytest
from app.models.developer import (
    AppCategory, AppStatus, AppVisibility, AppVersionReviewStatus,
    AutomationActionType, DeveloperStatus, InstallationStatus,
    RateLimitTier, SandboxExecutionStatus, UiSurface,
)
from app.models.webhook_delivery import DeliveryStatus

ALL_ENUMS = [
    AppCategory, AppStatus, AppVisibility, AppVersionReviewStatus,
    AutomationActionType, DeveloperStatus, InstallationStatus,
    RateLimitTier, SandboxExecutionStatus, UiSurface, DeliveryStatus,
]

@pytest.mark.parametrize("enum_cls", ALL_ENUMS, ids=lambda e: e.__name__)
def test_enum_is_str(enum_cls):
    for member in enum_cls:
        assert isinstance(member.value, str)

@pytest.mark.parametrize("enum_cls", ALL_ENUMS, ids=lambda e: e.__name__)
def test_enum_has_members(enum_cls):
    assert len(enum_cls) >= 2

@pytest.mark.parametrize("enum_cls", ALL_ENUMS, ids=lambda e: e.__name__)
def test_enum_values_unique(enum_cls):
    values = [m.value for m in enum_cls]
    assert len(values) == len(set(values))
