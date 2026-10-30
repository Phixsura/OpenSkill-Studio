from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_churn_predictor import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerChurnPredictor, ChurnSignals,
)

class TestConsumerChurnPredictor:
    def test_low_risk(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerChurnPredictor()
        svc.update_signals("inst-1", ChurnSignals(consumer_id="c1", requests_decline_pct=0, days_since_last_request=1))
        p = svc.predict("inst-1", "c1")
        assert p.risk_level == "low"

    def test_high_risk(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerChurnPredictor()
        svc.update_signals("inst-1", ChurnSignals(consumer_id="c1", requests_decline_pct=60, days_since_last_request=20, error_rate_increase_pct=30, support_tickets_open=5))
        p = svc.predict("inst-1", "c1")
        assert p.risk_level in ("high", "critical")

    def test_top_signal(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerChurnPredictor()
        svc.update_signals("inst-1", ChurnSignals(consumer_id="c1", requests_decline_pct=50))
        p = svc.predict("inst-1", "c1")
        assert p.top_signal == "usage_decline"

    def test_unknown_consumer(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerChurnPredictor()
        p = svc.predict("inst-1", "unknown")
        assert p.risk_level == "low"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerChurnPredictor()
        svc.update_signals("inst-1", ChurnSignals(consumer_id="c1"))
        assert len(svc.list_predictions("inst-2")) == 0
