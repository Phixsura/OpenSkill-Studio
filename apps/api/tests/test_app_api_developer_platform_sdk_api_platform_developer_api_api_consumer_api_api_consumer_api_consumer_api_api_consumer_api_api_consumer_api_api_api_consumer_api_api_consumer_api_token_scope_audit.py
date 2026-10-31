import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_api_consumer_api_api_consumer_api_token_scope_audit import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiTokenScopeAudit, ScopeUsageRecord,
)

class TestTokenScopeAudit:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_record_and_summary(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiTokenScopeAudit()
        svc.record("inst-1", ScopeUsageRecord(token_id="t1", consumer_id="c1", scope="read:users", endpoint="/api/users", granted=True, timestamp=self._now()))
        svc.record("inst-1", ScopeUsageRecord(token_id="t1", consumer_id="c1", scope="write:admin", endpoint="/api/admin", granted=False, timestamp=self._now()))
        summary = svc.get_summary("inst-1", "c1")
        assert summary.total_checks == 2 and summary.granted_count == 1 and summary.denied_count == 1

    def test_most_used_scope(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiTokenScopeAudit()
        for _ in range(5):
            svc.record("inst-1", ScopeUsageRecord(token_id="t1", consumer_id="c1", scope="read:users", endpoint="/api", granted=True, timestamp=self._now()))
        svc.record("inst-1", ScopeUsageRecord(token_id="t1", consumer_id="c1", scope="read:orders", endpoint="/api", granted=True, timestamp=self._now()))
        assert svc.get_summary("inst-1", "c1").most_used_scope == "read:users"

    def test_unused_scopes(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiTokenScopeAudit()
        svc.record("inst-1", ScopeUsageRecord(token_id="t1", consumer_id="c1", scope="read:users", endpoint="/api", granted=True, timestamp=self._now()))
        unused = svc.get_unused_scopes("inst-1", "c1", {"read:users", "write:users", "read:orders"})
        assert "write:users" in unused and "read:users" not in unused

    def test_denied_log(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiTokenScopeAudit()
        svc.record("inst-1", ScopeUsageRecord(token_id="t1", consumer_id="c1", scope="admin", endpoint="/api/admin", granted=False, timestamp=self._now()))
        denied = svc.get_denied_log("inst-1", "c1")
        assert len(denied) == 1 and denied[0].scope == "admin"

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiTokenScopeAudit()
        assert svc.get_summary("inst-1", "c1").total_checks == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiTokenScopeAudit()
        svc.record("inst-1", ScopeUsageRecord(token_id="t1", consumer_id="c1", scope="x", endpoint="/", granted=True, timestamp=self._now()))
        assert svc.get_summary("inst-2", "c1").total_checks == 0
