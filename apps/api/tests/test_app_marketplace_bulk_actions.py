from app.services.app_marketplace_bulk_actions import bulk_update_status, bulk_uninstall, validate_bulk_selection

def test_bulk_update():
    r = bulk_update_status(app_ids=["a1", "a2"], new_status="archived", actor_id="u1")
    assert r["count"] == 2
    assert all(x["status"] == "archived" for x in r["updated"])

def test_invalid_status():
    r = bulk_update_status(app_ids=["a1"], new_status="invalid", actor_id="u1")
    assert r["error"]

def test_bulk_uninstall():
    r = bulk_uninstall(installation_ids=["i1", "i2", "i3"], actor_id="u1")
    assert r["count"] == 3

def test_validate_ok():
    r = validate_bulk_selection(ids=["a1", "a2"])
    assert r["valid"]

def test_validate_empty():
    r = validate_bulk_selection(ids=[])
    assert not r["valid"]

def test_validate_too_many():
    r = validate_bulk_selection(ids=[f"a{i}" for i in range(100)], max_batch=50)
    assert not r["valid"]

def test_validate_duplicates():
    r = validate_bulk_selection(ids=["a1", "a1"])
    assert not r["valid"]
