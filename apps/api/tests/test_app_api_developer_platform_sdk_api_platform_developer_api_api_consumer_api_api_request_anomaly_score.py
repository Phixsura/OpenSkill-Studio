from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_anomaly_score import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestAnomalyScore

class TestRequestAnomalyScore:
    def test_normal_request(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestAnomalyScore()
        svc.set_baseline("inst-1", "c1", avg_latency_ms=50, avg_body_bytes=1024)
        s = svc.score("inst-1", "c1", "r1", latency_ms=55, body_bytes=1100, hour=14)
        assert s.anomaly_score < 0.4 and s.severity == "low"

    def test_anomalous_request(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestAnomalyScore()
        svc.set_baseline("inst-1", "c1", avg_latency_ms=50, avg_body_bytes=1024)
        s = svc.score("inst-1", "c1", "r1", latency_ms=500, body_bytes=50000, hour=3)
        assert s.is_anomalous is True

    def test_off_hours_factor(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestAnomalyScore()
        svc.set_baseline("inst-1", "c1", avg_latency_ms=50, avg_body_bytes=1024, typical_hour_start=9, typical_hour_end=17)
        s = svc.score("inst-1", "c1", "r1", latency_ms=50, body_bytes=1024, hour=3)
        assert "off_hours" in s.factors

    def test_no_baseline(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestAnomalyScore()
        s = svc.score("inst-1", "c1", "r1", latency_ms=100, body_bytes=500, hour=10)
        assert s.anomaly_score == 0.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestAnomalyScore()
        svc.set_baseline("inst-1", "c1", avg_latency_ms=50, avg_body_bytes=1024)
        svc.score("inst-1", "c1", "r1", 500, 50000, 3)
        assert svc.anomaly_count("inst-2") == 0
