from app.services.app_marketplace_audit_log import record_action, search_audit_log, summarize_audit_log

def test_record():
    r = record_action(actor_id="u1", action="delete_app", resource_type="app",
                      resource_id="a1", ip_address="1.2.3.4")
    assert r["log_id"].startswith("aud_")
    assert r["immutable"]

def test_search():
    entries = [{"actor_id": "u1", "action": "login"}, {"actor_id": "u2", "action": "delete_app"},
               {"actor_id": "u1", "action": "update_app"}]
    r = search_audit_log(entries=entries, actor_id="u1")
    assert r["total"] == 2

def test_summary():
    entries = [{"actor_id": "u1", "action": "login"}, {"actor_id": "u1", "action": "login"},
               {"actor_id": "u2", "action": "update_app"}]
    r = summarize_audit_log(entries=entries)
    assert r["unique_actors"] == 2
    assert r["top_actors"][0] == ("u1", 2)
