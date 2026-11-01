from app.services.app_marketplace_app_developer_api_status import get_api_status, build_status_badge_svg

def test_all_operational():
    eps = [{"path": "/users", "status": "operational"}, {"path": "/apps", "status": "operational"}]
    r = get_api_status(endpoints=eps)
    assert r["overall"] == "operational"

def test_degraded():
    eps = [{"path": "/users", "status": "operational"}, {"path": "/apps", "status": "degraded"}]
    r = get_api_status(endpoints=eps)
    assert r["overall"] == "degraded"

def test_badge():
    svg = build_status_badge_svg(status="operational")
    assert "#22c55e" in svg
