from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_outlier import detect_outliers

def test_outlier():
    r = detect_outliers([
        {"id": "i1", "error_rate_pct": 0.1}, {"id": "i2", "error_rate_pct": 0.2},
        {"id": "i3", "error_rate_pct": 0.15}, {"id": "i4", "error_rate_pct": 0.1},
        {"id": "i5", "error_rate_pct": 15.0},  # outlier
    ])
    assert r["ejections_needed"] >= 1
    assert r["outliers"][0]["instance"] == "i5"

def test_no_outlier():
    r = detect_outliers([
        {"id": "i1", "error_rate_pct": 0.1}, {"id": "i2", "error_rate_pct": 0.12},
        {"id": "i3", "error_rate_pct": 0.11},
    ])
    assert r["ejections_needed"] == 0
