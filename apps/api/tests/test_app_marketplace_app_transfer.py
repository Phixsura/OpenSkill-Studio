from app.services.app_marketplace_app_transfer import initiate_transfer, accept_transfer, reject_transfer

def test_initiate():
    r = initiate_transfer(app={"id": "a1", "status": "published"}, from_dev_id="d1", to_dev_id="d2", reason="Sold")
    assert r["status"] == "pending"

def test_self_transfer():
    r = initiate_transfer(app={"id": "a1", "status": "published"}, from_dev_id="d1", to_dev_id="d1", reason="X")
    assert r["error"]

def test_suspended():
    r = initiate_transfer(app={"id": "a1", "status": "suspended"}, from_dev_id="d1", to_dev_id="d2", reason="X")
    assert "suspended" in r["error"]

def test_accept():
    t = {"app_id": "a1", "from_developer_id": "d1", "to_developer_id": "d2", "status": "pending"}
    r = accept_transfer(transfer=t, accepting_dev_id="d2")
    assert r["status"] == "completed"

def test_accept_wrong_dev():
    t = {"app_id": "a1", "from_developer_id": "d1", "to_developer_id": "d2", "status": "pending"}
    r = accept_transfer(transfer=t, accepting_dev_id="d3")
    assert r["error"]

def test_reject():
    t = {"app_id": "a1", "from_developer_id": "d1", "to_developer_id": "d2", "status": "pending"}
    r = reject_transfer(transfer=t, rejecting_dev_id="d2")
    assert r["status"] == "rejected"
