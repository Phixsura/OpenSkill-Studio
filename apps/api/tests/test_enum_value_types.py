"""All developer enums use string values (str, Enum)."""

import pytest
from app.models.developer import (
    AppStatus, AppVisibility, AppVersionReviewStatus, InstallationStatus,
    SandboxExecutionStatus, DeveloperStatus, AppCategory, UiSurface,
    RateLimitTier, AutomationActionType,
)

ALL_ENUMS = [
    AppStatus, AppVisibility, AppVersionReviewStatus, InstallationStatus,
    SandboxExecutionStatus, DeveloperStatus, AppCategory, UiSurface,
    RateLimitTier, AutomationActionType,
]

@pytest.mark.parametrize("enum_cls", ALL_ENUMS, ids=lambda e: e.__name__)
def test_all_values_are_strings(enum_cls):
    for member in enum_cls:
        assert isinstance(member.value, str), f"{enum_cls.__name__}.{member.name} = {member.value!r} is not str"

@pytest.mark.parametrize("enum_cls", ALL_ENUMS, ids=lambda e: e.__name__)
def test_enum_is_str_subclass(enum_cls):
    assert issubclass(enum_cls, str)

@pytest.mark.parametrize("enum_cls", ALL_ENUMS, ids=lambda e: e.__name__)
def test_enum_non_empty(enum_cls):
    assert len(enum_cls) >= 2

def test_total_enum_count():
    assert len(ALL_ENUMS) == 10
