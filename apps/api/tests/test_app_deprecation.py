"""App deprecation scheduler tests."""

import pytest
from datetime import UTC, datetime, timedelta
from app.services.app_deprecation import create_deprecation_plan, check_sunset_status, format_deprecation_notice

def test_create_plan():
    p = create_deprecation_plan(app_id="a1", current_version="1.0.0")
    assert p["app_id"] == "a1"
    assert p["sunset_days"] == 90
    assert p["status"] == "active"

def test_create_with_replacement():
    p = create_deprecation_plan(app_id="a1", current_version="1.0.0", replacement_version="2.0.0")
    assert p["replacement_version"] == "2.0.0"

def test_custom_sunset_days():
    p = create_deprecation_plan(app_id="a1", current_version="1.0.0", sunset_days=30)
    assert p["sunset_days"] == 30

def test_check_active():
    future = (datetime.now(UTC) + timedelta(days=60)).isoformat()
    r = check_sunset_status(future)
    assert r["status"] == "active"

def test_check_approaching():
    future = (datetime.now(UTC) + timedelta(days=20)).isoformat()
    r = check_sunset_status(future)
    assert r["status"] == "approaching"

def test_check_imminent():
    future = (datetime.now(UTC) + timedelta(days=3)).isoformat()
    r = check_sunset_status(future)
    assert r["status"] == "imminent"

def test_check_expired():
    past = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    r = check_sunset_status(past)
    assert r["status"] == "expired"
    assert r["action"] == "revoke"

def test_format_notice():
    p = create_deprecation_plan(app_id="a1", current_version="1.0.0", replacement_version="2.0.0",
                                migration_guide_url="https://docs.example.com/migrate")
    notice = format_deprecation_notice(p)
    assert "1.0.0" in notice
    assert "2.0.0" in notice
    assert "docs.example.com" in notice

def test_format_notice_no_replacement():
    p = create_deprecation_plan(app_id="a1", current_version="1.0.0")
    notice = format_deprecation_notice(p)
    assert "1.0.0" in notice
    assert "upgrade" not in notice.lower()
