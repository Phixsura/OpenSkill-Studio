from app.services.app_api_developer_api_api_anomaly_detector import AppAPIDeveloperAPIApiAnomalyDetector

class TestAnomalyDetector:
    def test_no_anomaly(self):
        d = AppAPIDeveloperAPIApiAnomalyDetector()
        for i in range(10): d.add_sample("inst-1", "/api", "traffic", 100.0)
        a = d.detect("inst-1", "/api", "traffic", 105.0)
        assert a is None

    def test_detect_anomaly(self):
        d = AppAPIDeveloperAPIApiAnomalyDetector(warning_threshold=2.0)
        for i in range(20): d.add_sample("inst-1", "/api", "traffic", 100.0 + (i % 3))
        a = d.detect("inst-1", "/api", "traffic", 500.0)
        assert a is not None
        assert a.severity in ("warning", "critical")

    def test_too_few_samples(self):
        d = AppAPIDeveloperAPIApiAnomalyDetector()
        for i in range(3): d.add_sample("inst-1", "/api", "traffic", 100.0)
        assert d.detect("inst-1", "/api", "traffic", 500.0) is None

    def test_critical(self):
        d = AppAPIDeveloperAPIApiAnomalyDetector(warning_threshold=1.5, critical_threshold=2.0)
        for i in range(20): d.add_sample("inst-1", "/api", "latency", 50.0 + (i % 5))
        a = d.detect("inst-1", "/api", "latency", 1000.0)
        assert a is not None
        assert a.severity == "critical"

    def test_isolation(self):
        d = AppAPIDeveloperAPIApiAnomalyDetector()
        for i in range(10): d.add_sample("inst-1", "/api", "traffic", 100.0)
        assert d.critical_count("inst-2") == 0
