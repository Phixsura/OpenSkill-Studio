from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_outlier import detect_outliers

def test_outlier():
    instances = [{"id": f"i{i}", "error_rate_pct": 0.1} for i in range(10)]
    instances.append({"id": "bad", "error_rate_pct": 20.0})
    r = detect_outliers(instances)
    assert r["ejections_needed"] >= 1
    assert r["outliers"][0]["instance"] == "bad"

def test_no_outlier():
    r = detect_outliers([
        {"id": "i1", "error_rate_pct": 0.1}, {"id": "i2", "error_rate_pct": 0.12},
        {"id": "i3", "error_rate_pct": 0.11},
    ])
    assert r["ejections_needed"] == 0
