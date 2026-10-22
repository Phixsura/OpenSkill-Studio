"""App installation validator tests."""

import pytest
from app.services.app_install_validator import validate_installation

BASE = {"app_status": "published", "version_review_status": "approved",
        "already_installed": False, "required_permissions": ["read:cohorts"]}

def test_valid_install():
    r = validate_installation(**BASE)
    assert r["allowed"] is True
    assert r["errors"] == []

def test_not_published():
    r = validate_installation(**{**BASE, "app_status": "draft"})
    assert r["allowed"] is False

def test_not_approved():
    r = validate_installation(**{**BASE, "version_review_status": "pending"})
    assert r["allowed"] is False

def test_already_installed():
    r = validate_installation(**{**BASE, "already_installed": True})
    assert r["allowed"] is False

def test_denied_permissions():
    r = validate_installation(**{**BASE, "required_permissions": ["write:settings"],
                                 "org_allowed_permissions": ["read:cohorts"]})
    assert r["allowed"] is False

def test_high_priv_warning():
    r = validate_installation(**{**BASE, "required_permissions": ["run:background_jobs"]})
    assert r["allowed"] is True
    assert len(r["warnings"]) > 0

def test_no_org_filter():
    r = validate_installation(**{**BASE, "required_permissions": ["write:settings"]})
    assert r["allowed"] is True  # No org filter = allowed

def test_multiple_errors():
    r = validate_installation(app_status="draft", version_review_status="rejected",
                              already_installed=True, required_permissions=[])
    assert r["allowed"] is False
    assert len(r["errors"]) >= 3
