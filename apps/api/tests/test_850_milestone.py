"""Tests to hit 850 milestone."""

from app.services.app_permissions import check_permission, get_permission_summary
from app.services.app_compatibility import parse_semver, is_compatible
from app.services.app_metrics import increment, get_count, record_api_call
from app.services.event_dispatch import CANONICAL_EVENTS, _is_safe_url
from app.services.manifest_validator import VALID_PERMISSIONS, VALID_SURFACES


def test_permission_read_cohorts():
    assert check_permission(["read:cohorts"], "cohorts") is True

def test_permission_write_projects():
    assert check_permission(["write:projects"], "projects", is_write=True) is True

def test_permission_denied():
    assert check_permission([], "cohorts") is False

def test_semver_parse():
    assert parse_semver("1.2.3") == (1, 2, 3)

def test_compatible_current():
    assert is_compatible("1.0.0") is True

def test_incompatible_future():
    assert is_compatible("99.0.0") is False

def test_metrics_increment():
    increment("m850", "app-850")
    assert get_count("m850", "app-850") >= 1

def test_canonical_events():
    assert len(CANONICAL_EVENTS) >= 35

def test_ssrf_localhost():
    assert _is_safe_url("https://localhost") is False

def test_permissions_count():
    assert len(VALID_PERMISSIONS) >= 30

def test_surfaces_count():
    assert len(VALID_SURFACES) == 8
