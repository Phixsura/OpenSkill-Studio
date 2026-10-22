"""Parametrized upgrade compatibility scenarios."""

import pytest
from app.services.app_compatibility import check_upgrade_compatibility

SCENARIOS = [
    # (old, new, expected_compatible, description)
    ({"permissions": []}, {"permissions": []}, True, "empty→empty"),
    ({"permissions": ["read:cohorts"]}, {"permissions": ["read:cohorts"]}, True, "same perms"),
    ({"permissions": []}, {"permissions": ["read:cohorts"]}, True, "add perm"),
    ({"permissions": ["read:cohorts"]}, {"permissions": []}, True, "remove perm (not breaking)"),
    ({"schema_version": "1.0"}, {"schema_version": "1.0"}, True, "same schema"),
    ({"schema_version": "1.0"}, {"schema_version": "1.1"}, True, "minor schema bump"),
    ({"schema_version": "1.0"}, {"schema_version": "2.0"}, False, "major schema bump (breaking)"),
    ({"ui_extensions": [{"surface": "dashboard_card"}]}, {"ui_extensions": [{"surface": "dashboard_card"}]}, True, "same UI"),
    ({"ui_extensions": [{"surface": "dashboard_card"}]}, {"ui_extensions": []}, False, "remove UI surface"),
    (None, None, True, "both None"),
    (None, {"permissions": []}, True, "old None"),
    ({"permissions": []}, None, True, "new None"),
    ({"app": {"min_platform_version": "99.0.0"}}, {"app": {"min_platform_version": "99.0.0"}}, False, "incompatible platform"),
]

@pytest.mark.parametrize("old,new,expected,desc", SCENARIOS, ids=lambda x: x if isinstance(x, str) else "m")
def test_compatibility_scenario(old, new, expected, desc):
    r = check_upgrade_compatibility(old, new)
    assert r["compatible"] == expected, f"Failed: {desc}"
