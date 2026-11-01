from app.services.app_marketplace_app_app_app_app_app_app_app_comm_matrix import build_comm_matrix

def test_matrix():
    r = build_comm_matrix([
        {"source": "web", "destination": "api", "count": 1000},
        {"source": "api", "destination": "db", "count": 5000},
        {"source": "api", "destination": "cache", "count": 3000},
    ])
    assert r["total_communications"] == 9000
    assert len(r["services"]) == 4
    assert r["rows"][0]["service"] == "api"
