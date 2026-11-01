from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_error_recovery import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiErrorRecovery, RecoveryRule, RecoveryAction, RecoveryEvent,
)

class TestErrorRecovery:
    def test_custom_rule(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiErrorRecovery()
        svc.add_rule("inst-1", "c1", RecoveryRule(rule_id="r1", error_pattern="503", action=RecoveryAction.FALLBACK, fallback_endpoint="/backup"))
        assert svc.get_action("inst-1", "c1", 503) == RecoveryAction.FALLBACK

    def test_default_retry_for_500(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiErrorRecovery()
        assert svc.get_action("inst-1", "c1", 500) == RecoveryAction.RETRY

    def test_default_circuit_break_for_429(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiErrorRecovery()
        assert svc.get_action("inst-1", "c1", 429) == RecoveryAction.CIRCUIT_BREAK

    def test_recovery_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiErrorRecovery()
        svc.record_recovery("inst-1", RecoveryEvent(event_id="e1", consumer_id="c1", error_code=500, action_taken=RecoveryAction.RETRY, success=True))
        svc.record_recovery("inst-1", RecoveryEvent(event_id="e2", consumer_id="c1", error_code=500, action_taken=RecoveryAction.RETRY, success=False))
        assert svc.recovery_rate("inst-1") == 50.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiErrorRecovery()
        svc.add_rule("inst-1", "c1", RecoveryRule(rule_id="r1", error_pattern="500", action=RecoveryAction.RETRY))
        assert len(svc.list_rules("inst-2", "c1")) == 0
