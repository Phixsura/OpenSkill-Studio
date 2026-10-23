from app.services.app_marketplace_app_app_webhook_payload import build_payload, validate_payload

def test_build():
    r = build_payload(event_type="app.installed", resource_type="app", resource_id="app_123",
                      action="install", actor={"id": "u1", "name": "Alice"},
                      data={"version": "2.0.0"})
    assert r["id"].startswith("evt_")
    assert r["type"] == "app.installed"
    assert r["resource"]["id"] == "app_123"
    assert r["data"]["version"] == "2.0.0"

def test_validate_valid():
    p = build_payload(event_type="x", resource_type="y", resource_id="z", action="a", actor={"id": "u"})
    r = validate_payload(payload=p)
    assert r["valid"]

def test_validate_invalid():
    r = validate_payload(payload={"type": "x"})
    assert not r["valid"]
    assert len(r["missing"]) >= 3
