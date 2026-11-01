from app.services.app_marketplace_app_app_app_app_app_app_app_gw_middleware import create_middleware_chain, process_request

def test_chain():
    c = create_middleware_chain([
        {"name": "cors", "type": "transform"},
        {"name": "auth", "type": "auth"},
        {"name": "rate_limit", "type": "rate_limit", "enabled": False},
    ])
    assert c["total"] == 3
    assert c["enabled"] == 2

def test_process():
    c = create_middleware_chain([{"name": "cors"}, {"name": "log"}])
    r = process_request(c, {"path": "/api"})
    assert r["processed"]
    assert r["middleware_count"] == 2

def test_blocked():
    c = create_middleware_chain([{"name": "auth", "type": "auth"}])
    r = process_request(c, {"path": "/api"})  # no token
    assert not r["processed"]
    assert r["blocked_by"] == "auth"
