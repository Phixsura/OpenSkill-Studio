from app.services.app_marketplace_app_app_app_app_app_app_app_net_flow import analyze_flows

def test_flows():
    r = analyze_flows([
        {"src": "api", "dst": "db", "bytes": 5000, "packets": 50},
        {"src": "api", "dst": "db", "bytes": 3000, "packets": 30},
        {"src": "web", "dst": "api", "bytes": 10000, "packets": 100},
    ])
    assert r["unique_pairs"] == 2
    assert r["total_bytes"] == 18000
    assert r["top_flows"][0]["dst"] == "api"  # web→api has most bytes
