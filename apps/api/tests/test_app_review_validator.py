"""App review validator tests."""

import pytest
from app.services.app_review_validator import run_automated_review

VALID_MANIFEST = {
    "schema_version": "1.0",
    "app": {"name": "Test", "slug": "test-rv", "version": "1.0.0", "category": "connector"},
    "permissions": ["read:cohorts"],
}
HASH = "a" * 64

def test_passes_all():
    r = run_automated_review(manifest=VALID_MANIFEST, content_hash=HASH, version="1.0.0")
    assert r["passed"] is True
    assert r["score"] == 100

def test_invalid_manifest():
    r = run_automated_review(manifest={}, content_hash=HASH, version="1.0.0")
    assert r["passed"] is False

def test_bad_version():
    r = run_automated_review(manifest=VALID_MANIFEST, content_hash=HASH, version="abc")
    assert r["passed"] is False

def test_missing_hash():
    r = run_automated_review(manifest=VALID_MANIFEST, content_hash=None, version="1.0.0")
    assert r["passed"] is False

def test_short_hash():
    r = run_automated_review(manifest=VALID_MANIFEST, content_hash="abc", version="1.0.0")
    assert r["passed"] is False

def test_too_many_permissions():
    m = {**VALID_MANIFEST, "permissions": [f"read:resource_{i}" for i in range(25)]}
    r = run_automated_review(manifest=m, content_hash=HASH, version="1.0.0")
    assert any(not c["passed"] for c in r["checks"] if c["name"] == "permission_count")

def test_high_risk_warning():
    m = {**VALID_MANIFEST, "permissions": ["read:cohorts", "run:background_jobs"]}
    r = run_automated_review(manifest=m, content_hash=HASH, version="1.0.0")
    hr = next(c for c in r["checks"] if c["name"] == "high_risk_permissions")
    assert hr.get("warning") is True

def test_has_score():
    r = run_automated_review(manifest=VALID_MANIFEST, content_hash=HASH, version="1.0.0")
    assert 0 <= r["score"] <= 100

def test_checks_list():
    r = run_automated_review(manifest=VALID_MANIFEST, content_hash=HASH, version="1.0.0")
    assert len(r["checks"]) == 5
