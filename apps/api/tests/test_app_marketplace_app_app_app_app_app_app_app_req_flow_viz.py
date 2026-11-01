from app.services.app_marketplace_app_app_app_app_app_app_app_req_flow_viz import build_flow, flow_critical_path

def test_flow():
    r = build_flow([
        {"service": "gateway", "operation": "route", "duration_ms": 5},
        {"service": "api", "operation": "handle", "duration_ms": 50, "protocol": "gRPC"},
        {"service": "db", "operation": "query", "duration_ms": 20},
    ])
    assert r["depth"] == 3
    assert r["total_ms"] == 75
    assert len(r["nodes"]) == 3
    assert len(r["edges"]) == 2

def test_critical():
    r = flow_critical_path([
        {"service": "gateway", "duration_ms": 5},
        {"service": "api", "duration_ms": 50},
        {"service": "db", "duration_ms": 200},
    ])
    assert r["bottleneck"] == "db"
    assert r["bottleneck_ms"] == 200
