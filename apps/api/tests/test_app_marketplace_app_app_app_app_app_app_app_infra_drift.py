from app.services.app_marketplace_app_app_app_app_app_app_app_infra_drift import detect_drift, drift_summary

def test_drift():
    r = detect_drift({"replicas": 3, "cpu": "2", "memory": "4Gi"},
                       {"replicas": 5, "cpu": "2", "image": "old"})
    assert r["has_drift"]
    assert r["drift_count"] == 3  # replicas changed, memory missing, image extra

def test_summary():
    resources = [{"has_drift": True, "drift_count": 2}, {"has_drift": False, "drift_count": 0}]
    r = drift_summary(resources)
    assert r["drifted"] == 1
    assert r["drift_pct"] == 50
