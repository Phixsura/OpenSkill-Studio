"""Tests for Consumer API Endpoint Benchmark service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_benchmark import (
    EndpointBenchmark, BenchmarkRun,
)


class TestEndpointBenchmark:
    def _run(self, rid="r1", eid="ep1", n=100):
        latencies = [float(i + 10) for i in range(n)]
        return BenchmarkRun(rid, eid, n, 10.0, latencies, errors=2)

    def test_run_benchmark(self):
        svc = EndpointBenchmark()
        result = svc.run(self._run())
        assert result["rps"] == 10.0
        assert result["avg_ms"] > 0
        assert result["p95_ms"] > result["p50_ms"]

    def test_error_rate(self):
        svc = EndpointBenchmark()
        result = svc.run(self._run())
        assert result["error_rate"] == 2.0

    def test_compare_improved(self):
        svc = EndpointBenchmark()
        # Run A: slower
        svc.run(BenchmarkRun("r1", "ep1", 100, 10.0, [100.0] * 100))
        # Run B: faster
        svc.run(BenchmarkRun("r2", "ep1", 100, 10.0, [50.0] * 100))
        result = svc.compare("r1", "r2")
        assert result["improved"] is True
        assert result["latency_change_pct"] < 0

    def test_compare_regressed(self):
        svc = EndpointBenchmark()
        svc.run(BenchmarkRun("r1", "ep1", 100, 10.0, [50.0] * 100))
        svc.run(BenchmarkRun("r2", "ep1", 100, 10.0, [100.0] * 100))
        result = svc.compare("r1", "r2")
        assert result["latency_change_pct"] > 0

    def test_list_runs(self):
        svc = EndpointBenchmark()
        svc.run(self._run("r1", "ep1"))
        svc.run(self._run("r2", "ep2"))
        assert len(svc.list_runs()) == 2
        assert len(svc.list_runs(endpoint_id="ep1")) == 1

    def test_stats(self):
        svc = EndpointBenchmark()
        svc.run(self._run("r1", "ep1"))
        svc.run(self._run("r2", "ep2"))
        stats = svc.get_stats()
        assert stats["total_runs"] == 2
        assert stats["endpoints_benchmarked"] == 2

    def test_empty_latencies(self):
        svc = EndpointBenchmark()
        with pytest.raises(ValueError):
            svc.run(BenchmarkRun("r1", "ep1", 0, 1.0, []))

    def test_duplicate_run(self):
        svc = EndpointBenchmark()
        svc.run(self._run("r1"))
        with pytest.raises(ValueError):
            svc.run(self._run("r1"))

    def test_isolation(self):
        a, b = EndpointBenchmark(), EndpointBenchmark()
        a.run(self._run())
        assert b.get_stats()["total_runs"] == 0
