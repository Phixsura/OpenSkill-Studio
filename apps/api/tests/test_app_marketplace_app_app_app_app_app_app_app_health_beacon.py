from app.services.app_marketplace_app_app_app_app_app_app_app_health_beacon import (
    emit_beacon, aggregate_beacons, stale_services,
)

def test_emit():
    b = emit_beacon("api", "healthy", {"cpu": 45})
    assert b["service"] == "api"
    assert b["status"] == "healthy"
    assert len(b["beacon_id"]) == 10

def test_aggregate():
    beacons = [
        emit_beacon("api", "healthy"), emit_beacon("db", "healthy"),
        emit_beacon("cache", "degraded"),
    ]
    r = aggregate_beacons(beacons)
    assert r["unique_services"] == 3
    assert r["healthy_pct"] == 67
    assert not r["all_healthy"]

def test_stale():
    now = 1000.0
    beacons = [
        {"service": "api", "emitted_at": now - 30},
        {"service": "db", "emitted_at": now - 120},
    ]
    stale = stale_services(beacons, max_age_sec=60, now=now)
    assert "db" in stale
    assert "api" not in stale
