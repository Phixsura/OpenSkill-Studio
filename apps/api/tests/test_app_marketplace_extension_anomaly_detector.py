from app.services.app_marketplace_extension_anomaly_detector import AnomalyDetectorService


def test_zscore_normal():
    ad = AnomalyDetectorService()
    ad.add_points("cpu", [50 + i * 0.1 for i in range(100)])
    result = ad.detect_zscore("cpu", 52)
    assert result.is_anomaly is False
    assert result.severity == "normal"


def test_zscore_anomaly():
    ad = AnomalyDetectorService()
    ad.add_points("cpu", [50] * 100)  # very stable at 50
    ad.add_points("cpu", [51, 49, 50, 50])
    result = ad.detect_zscore("cpu", 99)  # way out
    assert result.is_anomaly is True
    assert result.direction == "high"


def test_iqr_normal():
    ad = AnomalyDetectorService()
    ad.add_points("latency", list(range(10, 60)))
    result = ad.detect_iqr("latency", 35)
    assert result.is_anomaly is False


def test_iqr_outlier():
    ad = AnomalyDetectorService()
    ad.add_points("latency", list(range(10, 60)))
    result = ad.detect_iqr("latency", 200)
    assert result.is_anomaly is True
    assert result.direction == "high"


def test_iqr_low_outlier():
    ad = AnomalyDetectorService()
    ad.add_points("temp", list(range(50, 100)))
    result = ad.detect_iqr("temp", -50)
    assert result.is_anomaly is True
    assert result.direction == "low"


def test_seasonal():
    ad = AnomalyDetectorService()
    # Normal traffic at 3pm: 100-120
    for _ in range(20):
        ad.add_point("traffic", 110, hour=15)
    # Anomaly at 3pm: 500 (way above normal for this hour)
    result = ad.detect_seasonal("traffic", 500, hour=15)
    assert result.is_anomaly is True
    assert result.method == "seasonal"


def test_insufficient_data():
    ad = AnomalyDetectorService()
    ad.add_points("new_metric", [1, 2, 3])
    result = ad.detect_zscore("new_metric", 100)
    assert result.is_anomaly is False  # not enough data to judge


def test_auto_detect():
    ad = AnomalyDetectorService()
    ad.add_points("metric", list(range(100)))
    result = ad.detect_auto("metric", 50)
    assert result.method in ("zscore", "iqr")


def test_severity_levels():
    ad = AnomalyDetectorService()
    data = [10.0] * 100
    ad.add_points("stable", data)
    mild = ad.detect_zscore("stable", 15)  # somewhat off
    extreme = ad.detect_zscore("stable", 100)  # very off
    assert extreme.severity == "critical" or extreme.is_anomaly


def test_score_returned():
    ad = AnomalyDetectorService()
    ad.add_points("x", [10] * 50 + [11] * 50)
    result = ad.detect_zscore("x", 50)
    assert result.score > 0
