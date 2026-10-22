"""App audit log service tests."""

import pytest
from app.services.app_audit_log import (
    record_audit_event, get_audit_log, get_audit_summary, clear_audit_log,
)

@pytest.fixture(autouse=True)
def _clean():
    clear_audit_log()
    yield
    clear_audit_log()

def test_record_returns_entry():
    e = record_audit_event(actor_id="u1", action="create", resource_type="app", resource_id="a1")
    assert e["actor_id"] == "u1"
    assert e["action"] == "create"
    assert "timestamp" in e

def test_get_returns_recorded():
    record_audit_event(actor_id="u1", action="create", resource_type="app", resource_id="a1", app_id="app-1")
    entries = get_audit_log(app_id="app-1")
    assert len(entries) == 1

def test_filter_by_action():
    record_audit_event(actor_id="u1", action="create", resource_type="app", resource_id="a1")
    record_audit_event(actor_id="u1", action="delete", resource_type="app", resource_id="a2")
    assert len(get_audit_log(action="create")) == 1
    assert len(get_audit_log(action="delete")) == 1

def test_filter_by_resource():
    record_audit_event(actor_id="u1", action="update", resource_type="app", resource_id="a1")
    record_audit_event(actor_id="u1", action="update", resource_type="key", resource_id="k1")
    assert len(get_audit_log(resource_type="app")) == 1

def test_filter_by_actor():
    record_audit_event(actor_id="u1", action="create", resource_type="app", resource_id="a1")
    record_audit_event(actor_id="u2", action="create", resource_type="app", resource_id="a2")
    assert len(get_audit_log(actor_id="u1")) == 1

def test_summary():
    record_audit_event(actor_id="u1", action="create", resource_type="app", resource_id="a1", app_id="sum-app")
    record_audit_event(actor_id="u1", action="update", resource_type="app", resource_id="a1", app_id="sum-app")
    record_audit_event(actor_id="u1", action="update", resource_type="app", resource_id="a1", app_id="sum-app")
    s = get_audit_summary("sum-app")
    assert s["total_events"] == 3
    assert s["action_counts"]["create"] == 1
    assert s["action_counts"]["update"] == 2

def test_summary_empty():
    s = get_audit_summary("nonexistent")
    assert s["total_events"] == 0

def test_limit():
    for i in range(100):
        record_audit_event(actor_id="u1", action="op", resource_type="x", resource_id=f"r{i}")
    entries = get_audit_log(limit=10)
    assert len(entries) == 10

def test_clear():
    record_audit_event(actor_id="u1", action="x", resource_type="x", resource_id="x")
    count = clear_audit_log()
    assert count == 1
    assert len(get_audit_log()) == 0

def test_actor_type():
    e = record_audit_event(actor_id="sys", actor_type="system", action="revoke", resource_type="app", resource_id="a1")
    assert e["actor_type"] == "system"

def test_details():
    e = record_audit_event(actor_id="u1", action="transition", resource_type="app", resource_id="a1",
                           details={"from": "draft", "to": "testing"})
    assert e["details"]["from"] == "draft"
