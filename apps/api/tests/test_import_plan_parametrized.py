"""Parametrized import plan tests."""

import pytest
from app.services.app_import import prepare_import_plan

PLANS = [
    ({"app": {"name": "A"}, "versions": [], "ui_extensions": []}, 0, 0),
    ({"app": {"name": "B"}, "versions": [{"version": "1.0.0"}], "ui_extensions": []}, 1, 0),
    ({"app": {"name": "C"}, "versions": [], "ui_extensions": [{"surface": "dashboard_card"}]}, 0, 1),
    ({"app": {"name": "D"}, "versions": [{"version": "1.0.0"}, {"version": "2.0.0"}], "ui_extensions": [{"surface": "dashboard_card"}, {"surface": "cohort_tool"}]}, 2, 2),
]

@pytest.mark.parametrize("data,ver_count,ext_count", PLANS)
def test_import_plan(data, ver_count, ext_count):
    plan = prepare_import_plan(data)
    assert plan["summary"]["app_count"] == 1
    assert plan["summary"]["version_count"] == ver_count
    assert plan["summary"]["ui_extension_count"] == ext_count
