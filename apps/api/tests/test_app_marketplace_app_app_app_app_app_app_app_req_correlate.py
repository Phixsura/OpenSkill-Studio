from app.services.app_marketplace_app_app_app_app_app_app_app_req_correlate import RequestCorrelator

def test_trace():
    rc = RequestCorrelator()
    cid = rc.start("req-001")["correlation_id"]
    rc.add_hop(cid, "gateway", "GET", "/api/users", 200, 5)
    rc.add_hop(cid, "user-svc", "GET", "/users", 200, 20)
    rc.add_hop(cid, "db", "SELECT", "users", 200, 10)
    t = rc.trace(cid)
    assert t["total_hops"] == 3
    assert t["success"]
    assert len(t["services"]) == 3
    assert t["total_ms"] == 35

def test_error():
    rc = RequestCorrelator()
    rc.add_hop("req-002", "api", "POST", "/orders", 500, 100)
    t = rc.trace("req-002")
    assert not t["success"]
    assert t["errors"] == 1
