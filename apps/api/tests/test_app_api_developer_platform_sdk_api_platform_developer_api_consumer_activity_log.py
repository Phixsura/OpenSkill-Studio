import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_consumer_activity_log import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerActivityLog, ActivityEntry,
)

class TestConsumerActivityLog:
    def test_record_and_query(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerActivityLog()
        svc.record("inst-1", ActivityEntry(entry_id="e1", consumer_id="c1", action="api_call", resource="/users", status_code=200))
        entries = svc.query("inst-1", consumer_id="c1")
        assert len(entries) == 1 and entries[0].resource == "/users"

    def test_filter_by_action(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerActivityLog()
        svc.record("inst-1", ActivityEntry(entry_id="e1", consumer_id="c1", action="api_call", resource="/a"))
        svc.record("inst-1", ActivityEntry(entry_id="e2", consumer_id="c1", action="key_created", resource="k1"))
        entries = svc.query("inst-1", action="key_created")
        assert len(entries) == 1

    def test_count_by_action(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerActivityLog()
        for i in range(3): svc.record("inst-1", ActivityEntry(entry_id=f"e{i}", consumer_id="c1", action="api_call", resource="/a"))
        svc.record("inst-1", ActivityEntry(entry_id="e9", consumer_id="c1", action="key_revoked", resource="k1"))
        counts = svc.count_by_action("inst-1")
        assert counts["api_call"] == 3 and counts["key_revoked"] == 1

    def test_unique_consumers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerActivityLog()
        svc.record("inst-1", ActivityEntry(entry_id="e1", consumer_id="c1", action="api_call", resource="/a"))
        svc.record("inst-1", ActivityEntry(entry_id="e2", consumer_id="c2", action="api_call", resource="/a"))
        svc.record("inst-1", ActivityEntry(entry_id="e3", consumer_id="c1", action="api_call", resource="/b"))
        assert svc.unique_consumers("inst-1") == 2

    def test_eviction(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerActivityLog(max_entries=100)
        for i in range(150): svc.record("inst-1", ActivityEntry(entry_id=f"e{i}", consumer_id="c1", action="api_call", resource="/a"))
        assert svc.total_entries("inst-1") == 100

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerActivityLog()
        svc.record("inst-1", ActivityEntry(entry_id="e1", consumer_id="c1", action="api_call", resource="/a"))
        assert svc.total_entries("inst-2") == 0
