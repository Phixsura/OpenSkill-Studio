from app.services.app_marketplace_app_app_app_app_app_app_app_sla_tracker import define_sla, check_sla, summarize_slas

def test_check():
    sla = define_sla("Uptime", 99.9, "availability")
    r = check_sla(sla, 99.95)
    assert r["met"]
    assert r["status"] == "met"
    r2 = check_sla(sla, 99.5)
    assert not r2["met"]
    assert r2["status"] == "breached"

def test_summary():
    results = [
        {"name": "Uptime", "met": True},
        {"name": "Latency", "met": False},
        {"name": "Error Rate", "met": True},
    ]
    s = summarize_slas(results)
    assert s["met"] == 2
    assert s["breached_count"] == 1
    assert "Latency" in s["breached_names"]
    assert s["compliance_pct"] == 67
