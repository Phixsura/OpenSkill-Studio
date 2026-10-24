from app.services.app_marketplace_app_metric_alert import check_metric_alert
def test_triggered():
    r = check_metric_alert(name="cpu", value=95, threshold=80, operator="gt")
    assert r["triggered"]
    assert r["status"] == "firing"
def test_ok():
    r = check_metric_alert(name="cpu", value=50, threshold=80, operator="gt")
    assert not r["triggered"]
