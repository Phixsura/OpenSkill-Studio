from app.services.app_marketplace_app_app_app_app_app_app_app_anomaly_score import z_score_detect, iqr_detect

def test_z_score():
    data = [10, 11, 10, 12, 10, 11, 10, 11, 10, 100]
    r = z_score_detect(data, threshold=2.0)
    assert len(r["anomalies"]) >= 1
    assert r["anomalies"][0]["value"] == 100

def test_no_anomaly():
    r = z_score_detect([10, 10, 10, 10, 10])
    assert len(r["anomalies"]) == 0

def test_iqr():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100]
    r = iqr_detect(data)
    assert len(r["outliers"]) >= 1
