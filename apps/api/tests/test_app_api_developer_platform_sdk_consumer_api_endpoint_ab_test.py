import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_endpoint_ab_test import (
    AppAPIDeveloperPlatformSDKConsumerApiEndpointAbTest, ABTest, ABTestVariant, ABTestResult,
)

class TestEndpointAbTest:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_create_and_start(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointAbTest()
        svc.create("inst-1", ABTest(test_id="t1", endpoint_path="/api/checkout", variants=[
            ABTestVariant(variant_id="a", name="Control", weight_pct=50, endpoint_version="v1"),
            ABTestVariant(variant_id="b", name="Experiment", weight_pct=50, endpoint_version="v2"),
        ]))
        svc.start("inst-1", "t1")
        tests = svc.list_tests("inst-1")
        assert len(tests) == 1 and tests[0].status == "running"

    def test_deterministic_assignment(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointAbTest()
        svc.create("inst-1", ABTest(test_id="t1", endpoint_path="/api", variants=[
            ABTestVariant(variant_id="a", name="A", weight_pct=50, endpoint_version="v1"),
            ABTestVariant(variant_id="b", name="B", weight_pct=50, endpoint_version="v2"),
        ]))
        svc.start("inst-1", "t1")
        a1 = svc.assign("inst-1", "t1", "consumer-xyz")
        a2 = svc.assign("inst-1", "t1", "consumer-xyz")
        assert a1.variant_id == a2.variant_id  # deterministic

    def test_invalid_weights(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointAbTest()
        with pytest.raises(ValueError, match="sum to 100"):
            svc.create("inst-1", ABTest(test_id="t1", endpoint_path="/api", variants=[
                ABTestVariant(variant_id="a", name="A", weight_pct=30, endpoint_version="v1"),
                ABTestVariant(variant_id="b", name="B", weight_pct=30, endpoint_version="v2"),
            ]))

    def test_results(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointAbTest()
        svc.record_result("inst-1", ABTestResult(test_id="t1", variant_id="a", requests=1000, errors=5, avg_latency_ms=50))
        svc.record_result("inst-1", ABTestResult(test_id="t1", variant_id="b", requests=1000, errors=20, avg_latency_ms=80))
        results = svc.get_results("inst-1", "t1")
        assert len(results) == 2

    def test_cannot_assign_stopped(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointAbTest()
        svc.create("inst-1", ABTest(test_id="t1", endpoint_path="/api", variants=[ABTestVariant(variant_id="a", name="A", weight_pct=100, endpoint_version="v1")]))
        with pytest.raises(ValueError, match="not running"):
            svc.assign("inst-1", "t1", "c1")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointAbTest()
        svc.create("inst-1", ABTest(test_id="t1", endpoint_path="/api", variants=[ABTestVariant(variant_id="a", name="A", weight_pct=100, endpoint_version="v1")]))
        assert len(svc.list_tests("inst-2")) == 0
