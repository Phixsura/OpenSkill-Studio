from app.services.app_extension_protocol import validate_inbound_message, build_context_message

def test_valid_message():
    assert validate_inbound_message({"type": "api_request", "payload": {"method": "GET", "path": "/cohorts"}}) == []

def test_missing_field():
    errors = validate_inbound_message({"type": "api_request", "payload": {"method": "GET"}})
    assert any("path" in e for e in errors)

def test_unknown_type():
    errors = validate_inbound_message({"type": "unknown"})
    assert len(errors) > 0

def test_ready():
    assert validate_inbound_message({"type": "ready", "payload": {}}) == []

def test_context():
    msg = build_context_message(org_id="o1", user_id="u1", surface="dashboard_card", permissions=["read:cohorts"])
    assert msg["type"] == "context"
    assert msg["payload"]["orgId"] == "o1"
