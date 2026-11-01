from app.services.app_marketplace_app_app_app_app_app_app_app_anomaly_alert import AnomalyAlertManager

def test_fire():
    aam = AnomalyAlertManager()
    r = aam.fire("high_cpu", "cpu_pct", 95, 80, "critical")
    assert r["fired"]
    # Suppressed on immediate re-fire
    r2 = aam.fire("high_cpu", "cpu_pct", 96, 80)
    assert not r2["fired"]

def test_acknowledge():
    aam = AnomalyAlertManager()
    aam.fire("err_spike", "error_rate", 10, 1)
    assert len(aam.active_alerts()) == 1
    aam.acknowledge("err_spike")
    assert len(aam.active_alerts()) == 0
