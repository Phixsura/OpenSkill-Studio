"""Event payload builder tests."""
from app.services.app_event_payload import build_event_payload, validate_event_payload

def test_build():
    p = build_event_payload(event_type="submission.completed", data={"id": "s1"}, org_id="o1")
    assert p["event_type"] == "submission.completed"
    assert p["event_id"].startswith("evt_")

def test_validate_valid():
    p = build_event_payload(event_type="app.installed", data={}, org_id="o1")
    assert validate_event_payload(p) == []

def test_validate_missing():
    assert len(validate_event_payload({})) > 0

def test_validate_bad_format():
    p = build_event_payload(event_type="noDot", data={}, org_id="o1")
    assert len(validate_event_payload(p)) > 0

def test_unique_ids():
    ids = {build_event_payload(event_type="t.e", data={}, org_id="o")["event_id"] for _ in range(20)}
    assert len(ids) == 20
