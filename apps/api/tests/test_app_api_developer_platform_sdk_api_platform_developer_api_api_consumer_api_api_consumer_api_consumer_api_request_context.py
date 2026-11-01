import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_request_context import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestContext,
)

class TestConsumerApiRequestContext:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_create(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestContext()
        ctx = svc.create("inst-1", "c1", attributes={"user": "admin"}, now=self._now())
        assert len(ctx.trace_id) == 32 and len(ctx.span_id) == 16 and ctx.attributes["user"] == "admin"

    def test_child_span(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestContext()
        parent = svc.create("inst-1", "c1", now=self._now())
        child = svc.create_child_span("inst-1", parent.context_id)
        assert child.trace_id == parent.trace_id and child.parent_span_id == parent.span_id and child.span_id != parent.span_id

    def test_add_attribute(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestContext()
        ctx = svc.create("inst-1", "c1", now=self._now())
        svc.add_attribute("inst-1", ctx.context_id, "method", "POST")
        assert svc.get("inst-1", ctx.context_id).attributes["method"] == "POST"

    def test_baggage_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestContext()
        ctx = svc.create("inst-1", "c1", now=self._now())
        for i in range(32):
            svc.add_baggage("inst-1", ctx.context_id, f"k{i}", f"v{i}")
        with pytest.raises(ValueError, match="Max 32"):
            svc.add_baggage("inst-1", ctx.context_id, "overflow", "x")

    def test_attribute_size_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestContext()
        ctx = svc.create("inst-1", "c1", now=self._now())
        with pytest.raises(ValueError, match="too long"):
            svc.add_attribute("inst-1", ctx.context_id, "k", "x" * 1025)

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestContext()
        ctx = svc.create("inst-1", "c1", now=self._now())
        assert svc.get("inst-2", ctx.context_id) is None
