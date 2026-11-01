from app.services.app_api_developer_platform_sdk_api_platform_api_consumer_churn_predictor import AppAPIDeveloperPlatformSDKApiPlatformApiConsumerChurnPredictor

class TestConsumerChurnPredictor:
    def test_low_risk(self):
        p = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerChurnPredictor()
        pred = p.predict("inst-1", "c1", days_since_last_call=1, api_calls_trend_pct=10, error_rate_pct=0.5)
        assert pred.risk_level == "low"

    def test_critical(self):
        p = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerChurnPredictor()
        pred = p.predict("inst-1", "c1", days_since_last_call=60, api_calls_trend_pct=-80, error_rate_pct=15, support_tickets_open=5)
        assert pred.risk_level == "critical"

    def test_at_risk(self):
        p = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerChurnPredictor()
        p.predict("inst-1", "c1", days_since_last_call=1)
        p.predict("inst-1", "c2", days_since_last_call=60, api_calls_trend_pct=-80)
        assert len(p.at_risk("inst-1", "high")) == 1

    def test_isolation(self):
        p = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerChurnPredictor()
        p.predict("inst-1", "c1", days_since_last_call=60)
        assert len(p.all_predictions("inst-2")) == 0
