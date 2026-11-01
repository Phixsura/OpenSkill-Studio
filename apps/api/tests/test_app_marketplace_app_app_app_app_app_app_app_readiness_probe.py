from app.services.app_marketplace_app_app_app_app_app_app_app_readiness_probe import probe_readiness, readiness_report

def test_probe():
    r = probe_readiness([
        {"name": "api", "checks": {"database": True, "cache": True, "config_loaded": True}},
        {"name": "worker", "checks": {"database": True, "cache": True, "config_loaded": False}},
    ])
    assert r["ready"] == 1
    assert not r["all_ready"]

def test_report():
    probes = [{"all_ready": True, "total": 3, "ready": 3},
              {"all_ready": False, "total": 2, "ready": 1}]
    r = readiness_report(probes)
    assert r["readiness_pct"] == 80
    assert not r["all_ready"]
