from app.services.app_marketplace_app_app_app_app_app_app_app_circuit_health import fleet_circuit_health, recovery_estimate

def test_healthy():
    r = fleet_circuit_health([
        {"service": "api", "state": "closed"},
        {"service": "db", "state": "closed"},
    ])
    assert r["overall"] == "healthy"
    assert r["open_pct"] == 0

def test_critical():
    r = fleet_circuit_health([
        {"service": "api", "state": "closed"},
        {"service": "payment", "state": "open", "critical": True},
    ])
    assert r["overall"] == "critical"
    assert "payment" in r["critical_open"]

def test_recovery():
    r = recovery_estimate({"service": "db", "state": "open", "recovery_seconds": 30, "elapsed_seconds": 20})
    assert r["needs_recovery"]
    assert r["remaining_seconds"] == 10
