from app.services.app_marketplace_app_app_app_app_app_app_app_sl_report import generate_sl_report, executive_summary

def test_report():
    r = generate_sl_report([
        {"name": "Uptime", "actual_pct": 99.95, "target_pct": 99.9},
        {"name": "Latency", "actual_pct": 99.0, "target_pct": 99.9},
        {"name": "Error Rate", "actual_pct": 99.99, "target_pct": 99.5},
    ])
    assert r["met"] == 2
    assert r["compliance_pct"] == 67

def test_summary():
    report = generate_sl_report([{"name": "x", "actual_pct": 100, "target_pct": 99.9}])
    s = executive_summary(report)
    assert s["grade"] == "A"
    assert "1/1" in s["summary"]
