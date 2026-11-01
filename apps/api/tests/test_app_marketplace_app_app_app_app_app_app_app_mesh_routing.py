from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_routing import evaluate_route, weighted_split

def test_match_rule():
    r = evaluate_route(
        {"path": "/api/v2/users", "method": "GET"},
        [{"name": "v2", "conditions": [{"field": "path", "op": "prefix", "value": "/api/v2"}],
          "destination": "api-v2"}])
    assert r["matched"]
    assert r["destination"] == "api-v2"

def test_no_match():
    r = evaluate_route({"path": "/health"}, [
        {"name": "v2", "conditions": [{"field": "path", "op": "prefix", "value": "/api/v2"}],
         "destination": "api-v2"}])
    assert not r["matched"]
    assert r["destination"] == "default"

def test_weighted():
    r = weighted_split([
        {"destination": "canary", "weight": 10},
        {"destination": "stable", "weight": 90},
    ])
    assert r["destinations"][0]["pct"] == 10.0
    assert r["destinations"][1]["pct"] == 90.0
