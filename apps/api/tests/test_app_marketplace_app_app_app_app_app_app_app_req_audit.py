from app.services.app_marketplace_app_app_app_app_app_app_app_req_audit import RequestAuditLogger

def test_log_query():
    ral = RequestAuditLogger()
    ral.log("u1", "GET", "/api/users", 200)
    ral.log("u1", "POST", "/api/orders", 201)
    ral.log("u2", "GET", "/api/users", 403)
    r = ral.query(user_id="u1")
    assert len(r) == 2
    r2 = ral.query(status_gte=400)
    assert len(r2) == 1
    s = ral.stats()
    assert s["unique_users"] == 2
