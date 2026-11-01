import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_endpoint_api_consumer_api_request_flow_analyzer import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiRequestFlowAnalyzer, RequestFlow, FlowStep,
)

class TestRequestFlowAnalyzer:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_record_and_analyze(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiRequestFlowAnalyzer()
        svc.record_flow("inst-1", RequestFlow(flow_id="f1", consumer_id="c1", endpoint="/api/orders", total_latency_ms=150, steps=[
            FlowStep(step_id="s1", name="Auth", service="auth-svc", latency_ms=20, order=1),
            FlowStep(step_id="s2", name="DB Query", service="db", latency_ms=100, order=2),
            FlowStep(step_id="s3", name="Response", service="gateway", latency_ms=30, order=3),
        ], timestamp=self._now()))
        analysis = svc.analyze("inst-1", "c1")
        assert analysis.total_flows == 1 and analysis.bottleneck_service == "db"

    def test_slowest_step(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiRequestFlowAnalyzer()
        svc.record_flow("inst-1", RequestFlow(flow_id="f1", consumer_id="c1", endpoint="/api", total_latency_ms=200, steps=[
            FlowStep(step_id="s1", name="Serialize", service="app", latency_ms=150, order=1),
            FlowStep(step_id="s2", name="Send", service="net", latency_ms=50, order=2),
        ]))
        assert svc.analyze("inst-1", "c1").slowest_step == "Serialize"

    def test_error_count(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiRequestFlowAnalyzer()
        svc.record_flow("inst-1", RequestFlow(flow_id="f1", consumer_id="c1", endpoint="/api", total_latency_ms=100, steps=[
            FlowStep(step_id="s1", name="Auth", service="auth", latency_ms=50, status="error"),
        ]))
        assert svc.analyze("inst-1", "c1").error_count == 1

    def test_recent(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiRequestFlowAnalyzer()
        svc.record_flow("inst-1", RequestFlow(flow_id="f1", consumer_id="c1", endpoint="/a", total_latency_ms=50, timestamp=self._now()))
        svc.record_flow("inst-1", RequestFlow(flow_id="f2", consumer_id="c1", endpoint="/b", total_latency_ms=100, timestamp=self._now()))
        recent = svc.get_recent("inst-1", "c1")
        assert len(recent) == 2 and recent[0].flow_id == "f2"

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiRequestFlowAnalyzer()
        assert svc.analyze("inst-1", "c1").total_flows == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiRequestFlowAnalyzer()
        svc.record_flow("inst-1", RequestFlow(flow_id="f1", consumer_id="c1", endpoint="/api", total_latency_ms=50))
        assert svc.analyze("inst-2", "c1").total_flows == 0
