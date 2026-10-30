from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_access_audit import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiAccessAudit, AccessAttempt,
)

class TestConsumerApiAccessAudit:
    def test_record_and_query(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiAccessAudit()
        svc.record("inst-1", AccessAttempt(attempt_id="a1", consumer_id="c1", endpoint="/api", method="GET", granted=True, reason="authorized"))
        svc.record("inst-1", AccessAttempt(attempt_id="a2", consumer_id="c1", endpoint="/admin", method="DELETE", granted=False, reason="scope_denied"))
        denied = svc.denied_attempts("inst-1")
        assert len(denied) == 1

    def test_denial_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiAccessAudit()
        svc.record("inst-1", AccessAttempt(attempt_id="a1", consumer_id="c1", endpoint="/a", method="GET", granted=True))
        svc.record("inst-1", AccessAttempt(attempt_id="a2", consumer_id="c1", endpoint="/b", method="GET", granted=False, reason="rate_limited"))
        assert svc.denial_rate("inst-1") == 50.0

    def test_by_reason(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiAccessAudit()
        svc.record("inst-1", AccessAttempt(attempt_id="a1", consumer_id="c1", endpoint="/a", method="GET", granted=False, reason="rate_limited"))
        svc.record("inst-1", AccessAttempt(attempt_id="a2", consumer_id="c1", endpoint="/b", method="GET", granted=False, reason="rate_limited"))
        svc.record("inst-1", AccessAttempt(attempt_id="a3", consumer_id="c1", endpoint="/c", method="GET", granted=False, reason="ip_blocked"))
        reasons = svc.by_reason("inst-1")
        assert reasons["rate_limited"] == 2 and reasons["ip_blocked"] == 1

    def test_eviction(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiAccessAudit(max_entries=1000)
        for i in range(1500): svc.record("inst-1", AccessAttempt(attempt_id=f"a{i}", consumer_id="c1", endpoint="/a", method="GET", granted=True))
        assert svc.total_entries("inst-1") == 1000

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiAccessAudit()
        svc.record("inst-1", AccessAttempt(attempt_id="a1", consumer_id="c1", endpoint="/a", method="GET", granted=True))
        assert svc.total_entries("inst-2") == 0
