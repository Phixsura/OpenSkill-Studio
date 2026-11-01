from app.services.app_marketplace_app_app_app_app_app_app_app_gw_circuit_stats import gateway_circuit_stats

def test_stats():
    r = gateway_circuit_stats([
        {"backend": "api", "event": "trip"},
        {"backend": "api", "event": "blocked"},
        {"backend": "api", "event": "blocked"},
        {"backend": "api", "event": "recover"},
        {"backend": "db", "event": "trip"},
    ])
    assert r["total_trips"] == 2
    assert r["total_blocked"] == 2
    assert r["backends_affected"] == 2
    api = [b for b in r["backends"] if b["backend"] == "api"][0]
    assert api["trips"] == 1
    assert api["requests_blocked"] == 2
