import json
from app.services.app_webhook_payload_builder import build_delivery_payload, parse_delivery_payload

def test_build():
    raw = build_delivery_payload(event_type="app.installed", event_id="e1", data={"x": 1},
                                  app_id="a1", installation_id="i1", org_id="o1")
    assert isinstance(raw, bytes)
    parsed = json.loads(raw)
    assert parsed["event"] == "app.installed"
    assert parsed["api_version"] == "2024-01-01"

def test_parse_valid():
    raw = build_delivery_payload(event_type="t", event_id="e", data={}, app_id="a", installation_id="i", org_id="o")
    result = parse_delivery_payload(raw)
    assert result is not None
    assert result["event"] == "t"

def test_parse_invalid():
    assert parse_delivery_payload(b"not json") is None

def test_compact_json():
    raw = build_delivery_payload(event_type="t", event_id="e", data={}, app_id="a", installation_id="i", org_id="o")
    assert b" " not in raw  # Compact separators
