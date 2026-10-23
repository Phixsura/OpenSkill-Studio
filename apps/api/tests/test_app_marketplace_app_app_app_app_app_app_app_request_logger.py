from app.services.app_marketplace_app_app_app_app_app_app_app_request_logger import RequestLogger

def test_logger():
    rl = RequestLogger(max_entries=100)
    rl.log(method="GET", path="/api/users", status=200, duration_ms=50, user_id="u1")
    rl.log(method="POST", path="/api/apps", status=201, duration_ms=120)
    rl.log(method="GET", path="/api/users/1", status=404, duration_ms=30)
    q = rl.query(status_min=400)
    assert len(q) == 1
    assert q[0]["status"] == 404
    q2 = rl.query(path_prefix="/api/users")
    assert len(q2) == 2
    s = rl.stats()
    assert s["total"] == 3
    assert s["errors"] == 1
