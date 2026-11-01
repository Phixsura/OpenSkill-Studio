from app.services.app_marketplace_app_app_app_app_app_app_app_health_attest import HealthAttestation
import time

def test_attest():
    ha = HealthAttestation(stale_seconds=30)
    ha.attest("api", "healthy", {"version": "2.0"})
    r = ha.check("api")
    assert r["status"] == "healthy"
    assert not r["stale"]

def test_stale():
    ha = HealthAttestation(stale_seconds=10)
    ha.attest("api", "healthy")
    r = ha.check("api", now=time.time() + 15)
    assert r["stale"]
    assert r["status"] == "stale"

def test_all():
    ha = HealthAttestation()
    ha.attest("api", "healthy")
    ha.attest("db", "degraded")
    r = ha.all_services()
    assert r["total"] == 2
    assert r["healthy"] == 1
