from app.services.app_developer_app_transfer import create_transfer_request, validate_transfer

def test_create():
    r = create_transfer_request(app_id="a1", from_developer="d1", to_developer="d2")
    assert r["status"] == "pending"

def test_validate_ok():
    r = create_transfer_request(app_id="a1", from_developer="d1", to_developer="d2")
    assert validate_transfer(r) == []

def test_validate_self():
    r = create_transfer_request(app_id="a1", from_developer="d1", to_developer="d1")
    assert len(validate_transfer(r)) > 0
