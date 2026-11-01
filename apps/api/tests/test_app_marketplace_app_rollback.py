from app.services.app_marketplace_app_rollback import can_rollback, execute_rollback, build_rollback_confirmation

def test_can():
    r = can_rollback(installation={"app_version_id": "v2"},
                      available_versions=[{"id": "v1", "review_status": "approved", "released_at": "2026-01-01"},
                                          {"id": "v2", "review_status": "approved", "released_at": "2026-06-01"}])
    assert r["can_rollback"]
    assert r["target_version"]["id"] == "v1"

def test_cannot():
    r = can_rollback(installation={"app_version_id": "v1"},
                      available_versions=[{"id": "v1", "review_status": "approved"}])
    assert not r["can_rollback"]

def test_execute():
    r = execute_rollback(installation_id="i1", target_version_id="v1", reason="Bug in v2")
    assert r["status"] == "rolled_back"

def test_confirmation():
    c = build_rollback_confirmation(app_name="App", from_version="2.0", to_version="1.0")
    assert "1.0" in c["message"]
    assert len(c["warnings"]) == 2
