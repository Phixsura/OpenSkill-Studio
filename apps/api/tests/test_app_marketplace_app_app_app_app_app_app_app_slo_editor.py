from app.services.app_marketplace_app_app_app_app_app_app_app_slo_editor import create_slo, validate_slo, slo_catalog

def test_create():
    r = create_slo("Uptime", "availability", 99.9)
    assert r["error_budget_pct"] == 0.1
    assert r["window_days"] == 30

def test_validate():
    slo = create_slo("Bad", "x", 80)
    r = validate_slo(slo)
    assert not r["valid"]
    assert r["issue_count"] >= 1

def test_catalog():
    slos = [create_slo("A", "availability", 99.9), create_slo("B", "latency", 99.0)]
    r = slo_catalog(slos)
    assert r["total"] == 2
    assert r["avg_target"] == 99.45
