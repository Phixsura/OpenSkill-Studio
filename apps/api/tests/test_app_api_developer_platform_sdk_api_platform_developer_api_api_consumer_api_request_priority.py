import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_request_priority import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestPriority, PriorityConfig,
)

class TestRequestPriority:
    def test_set_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestPriority()
        svc.set_priority("inst-1", PriorityConfig(consumer_id="c1", priority_level=8, queue_position="high"))
        assert svc.get_priority("inst-1", "c1") == 8

    def test_default_priority(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestPriority()
        assert svc.get_priority("inst-1", "unknown") == 5

    def test_preempt(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestPriority()
        svc.set_priority("inst-1", PriorityConfig(consumer_id="c1", priority_level=10, queue_position="critical"))
        assert svc.should_preempt("inst-1", "c1") is True

    def test_sorted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestPriority()
        svc.set_priority("inst-1", PriorityConfig(consumer_id="c1", priority_level=3))
        svc.set_priority("inst-1", PriorityConfig(consumer_id="c2", priority_level=9))
        sorted_list = svc.sorted_consumers("inst-1")
        assert sorted_list[0].consumer_id == "c2"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestPriority()
        svc.set_priority("inst-1", PriorityConfig(consumer_id="c1", priority_level=5))
        assert len(svc.list_configs("inst-2")) == 0
