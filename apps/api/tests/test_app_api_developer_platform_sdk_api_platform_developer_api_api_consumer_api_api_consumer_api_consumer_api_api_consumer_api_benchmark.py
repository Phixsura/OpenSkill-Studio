import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_benchmark import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiBenchmark, BenchmarkConfig,
)

class TestConsumerApiBenchmark:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_run(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiBenchmark()
        result = svc.run("inst-1", "c1", BenchmarkConfig(benchmark_id="b1", endpoint_path="/api/users", total_requests=100), self._now())
        assert result.total_requests == 100 and result.avg_latency_ms > 0

    def test_history(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiBenchmark()
        svc.run("inst-1", "c1", BenchmarkConfig(benchmark_id="b1", endpoint_path="/api"), self._now())
        svc.run("inst-1", "c1", BenchmarkConfig(benchmark_id="b1", endpoint_path="/api"), self._now())
        history = svc.get_history("inst-1", "c1", "b1")
        assert len(history) == 2

    def test_compare(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiBenchmark()
        svc.run("inst-1", "c1", BenchmarkConfig(benchmark_id="b1", endpoint_path="/api"), self._now())
        svc.run("inst-1", "c1", BenchmarkConfig(benchmark_id="b1", endpoint_path="/api"), self._now())
        diff = svc.compare_latest("inst-1", "c1", "b1")
        assert diff is not None and "latency_change_pct" in diff

    def test_no_compare_single(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiBenchmark()
        svc.run("inst-1", "c1", BenchmarkConfig(benchmark_id="b1", endpoint_path="/api"), self._now())
        assert svc.compare_latest("inst-1", "c1", "b1") is None

    def test_invalid_concurrency(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiBenchmark()
        with pytest.raises(ValueError, match="concurrency"):
            svc.run("inst-1", "c1", BenchmarkConfig(benchmark_id="b1", endpoint_path="/api", concurrency=0), self._now())

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiBenchmark()
        svc.run("inst-1", "c1", BenchmarkConfig(benchmark_id="b1", endpoint_path="/api"), self._now())
        assert len(svc.get_history("inst-2", "c1", "b1")) == 0
