from app.services.app_marketplace_app_app_app_app_app_app_app_readiness_chk import check_readiness

def test_ready():
    statuses = {k: True for k in ["database", "cache", "api", "auth", "backups", "ssl_certs", "dns", "monitoring", "logging", "ci_cd"]}
    r = check_readiness(statuses)
    assert r["launch_ready"]
    assert r["readiness_pct"] == 100

def test_not_ready():
    statuses = {"database": True, "api": True, "auth": False}
    r = check_readiness(statuses)
    assert not r["launch_ready"]
    assert r["critical_pass"] < r["critical_total"]
