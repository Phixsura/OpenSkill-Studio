from app.services.app_marketplace_app_app_app_app_app_app_app_health_probe import HealthProbe

def test_probes():
    hp = HealthProbe()
    assert hp.liveness()["status"] == "ok"
    assert hp.startup()["status"] == "in_progress"
    assert hp.readiness()["status"] == "not_ready"
    hp.mark_started()
    assert hp.startup()["status"] == "complete"

def test_readiness_checks():
    hp = HealthProbe()
    hp.mark_started()
    hp.register_check("db", lambda: True, "readiness")
    hp.register_check("cache", lambda: False, "readiness")
    r = hp.readiness()
    assert r["status"] == "not_ready"
    assert "cache" in r["failed_checks"]
