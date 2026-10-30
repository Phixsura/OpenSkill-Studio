from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_anomaly_detector import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiAnomalyDetector

class TestAnomalyDetector:
    def test_no_anomaly_within_threshold(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiAnomalyDetector(threshold_pct=50)
        svc.set_baseline("inst-1", "c1", "requests", 1000)
        assert svc.check("inst-1", "c1", "requests", 1200) is None  # 20% deviation

    def test_anomaly_above_threshold(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiAnomalyDetector(threshold_pct=50)
        svc.set_baseline("inst-1", "c1", "requests", 1000)
        alert = svc.check("inst-1", "c1", "requests", 2000)
        assert alert is not None and alert.deviation_pct == 100.0

    def test_severity_levels(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiAnomalyDetector(threshold_pct=10)
        svc.set_baseline("inst-1", "c1", "errors", 10)
        alert = svc.check("inst-1", "c1", "errors", 50)  # 300% deviation
        assert alert.severity == "high"

    def test_no_baseline(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiAnomalyDetector()
        assert svc.check("inst-1", "c1", "requests", 1000) is None

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiAnomalyDetector()
        svc.set_baseline("inst-1", "c1", "x", 100)
        svc.check("inst-1", "c1", "x", 500)
        assert svc.alert_count("inst-2") == 0
