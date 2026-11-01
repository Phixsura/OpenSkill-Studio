from app.services.app_marketplace_app_app_app_app_app_app_app_metric_alerts import create_alert, evaluate_alert, evaluate_all

def test_create():
    a = create_alert("High CPU", "cpu_pct", ">", 90.0, severity="critical")
    assert a["created"]
    assert a["threshold"] == 90.0

def test_evaluate():
    a = create_alert("", "x", ">", 80.0)
    r = evaluate_alert(a, 95.0)
    assert r["triggered"]
    r2 = evaluate_alert(a, 50.0)
    assert not r2["triggered"]

def test_evaluate_all():
    alerts = [
        create_alert("CPU", "cpu", ">", 90),
        create_alert("Mem", "mem", ">", 80),
    ]
    r = evaluate_all(alerts, {"cpu": 95, "mem": 60})
    assert r["fired"] == 1
    assert not r["all_clear"]
