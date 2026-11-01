from app.services.app_marketplace_app_app_app_app_app_app_app_req_logger import RequestLogger

def test_log_query():
    rl = RequestLogger()
    rl.log("GET", "/api/users", 200, 15)
    rl.log("POST", "/api/users", 201, 30)
    rl.log("GET", "/api/orders", 500, 100)
    errors = rl.query(status_gte=400)
    assert len(errors) == 1
    api = rl.query(path_prefix="/api/users")
    assert len(api) == 2

def test_stats():
    rl = RequestLogger()
    rl.log("GET", "/", 200, 5)
    rl.log("GET", "/", 404, 5)
    s = rl.stats()
    assert s["by_status"]["2xx"] == 1
    assert s["by_status"]["4xx"] == 1
