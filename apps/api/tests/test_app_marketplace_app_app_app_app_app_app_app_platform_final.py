from app.services.app_marketplace_app_app_app_app_app_app_app_platform_final import platform_final_status

def test_operational():
    r = platform_final_status(
        [{"name": m, "status": "operational"} for m in ["SDK", "Apps", "Market", "API", "Eco",
                                                         "Portal", "Security", "Infra", "Obs", "Ops"]],
        {"uptime_pct": 99.99, "error_rate_pct": 0.1, "rps": 10000, "p99_ms": 100})
    assert r["overall"] == "fully_operational"
    assert r["score"] == 100
    assert r["modules_operational"] == 10

def test_degraded():
    mods = [{"name": "SDK", "status": "operational"}] * 8 + [{"name": "x", "status": "degraded"}] * 2
    r = platform_final_status(mods, {"uptime_pct": 99.5, "error_rate_pct": 5, "rps": 5000, "p99_ms": 800})
    assert r["overall"] == "critical"
