from app.services.app_marketplace_app_app_app_app_app_app_app_peak_detect import detect_peaks

def test_peaks():
    traffic = [{"hour": i, "rps": 100} for i in range(20)]
    traffic.append({"hour": 20, "rps": 500})
    traffic.append({"hour": 21, "rps": 600})
    r = detect_peaks(traffic)
    assert len(r["peaks"]) >= 2
    assert r["max_rps"] == 600

def test_no_peaks():
    traffic = [{"hour": i, "rps": 100 + i} for i in range(24)]
    r = detect_peaks(traffic)
    assert r["avg_rps"] > 0
