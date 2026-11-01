"""Tests for Consumer API Endpoint Health Score service."""
from app.services.app_api_developer_platform_sdk_consumer_api_health_score import (
    EndpointHealthScorer, HealthInput,
)


class TestEndpointHealthScorer:
    def test_perfect_score(self):
        svc = EndpointHealthScorer()
        result = svc.score(HealthInput("ep1", availability_pct=100, latency_p95_ms=50,
                                        latency_target_ms=200, error_rate_pct=0,
                                        throughput_rps=150, throughput_target_rps=100))
        assert result["composite_score"] >= 90
        assert result["grade"] == "A"

    def test_degraded_score(self):
        svc = EndpointHealthScorer()
        result = svc.score(HealthInput("ep1", availability_pct=95, latency_p95_ms=300,
                                        latency_target_ms=200, error_rate_pct=3,
                                        throughput_rps=80, throughput_target_rps=100))
        assert result["grade"] in ("B", "C")

    def test_poor_score(self):
        svc = EndpointHealthScorer()
        result = svc.score(HealthInput("ep1", availability_pct=80, latency_p95_ms=500,
                                        latency_target_ms=100, error_rate_pct=10,
                                        throughput_rps=20, throughput_target_rps=100))
        assert result["grade"] in ("D", "F")

    def test_components(self):
        svc = EndpointHealthScorer()
        result = svc.score(HealthInput("ep1", availability_pct=99.9))
        assert "availability" in result["components"]
        assert "latency" in result["components"]
        assert "error_rate" in result["components"]
        assert "throughput" in result["components"]

    def test_ranking(self):
        svc = EndpointHealthScorer()
        svc.score(HealthInput("ep1", availability_pct=99, throughput_rps=100, throughput_target_rps=100))
        svc.score(HealthInput("ep2", availability_pct=80, error_rate_pct=5, throughput_rps=50, throughput_target_rps=100))
        ranking = svc.get_ranking()
        assert ranking[0]["endpoint_id"] == "ep1"
        assert ranking[0]["rank"] == 1

    def test_get_score(self):
        svc = EndpointHealthScorer()
        svc.score(HealthInput("ep1"))
        assert svc.get_score("ep1") is not None
        assert svc.get_score("missing") is None

    def test_summary(self):
        svc = EndpointHealthScorer()
        svc.score(HealthInput("ep1", availability_pct=100, throughput_rps=100, throughput_target_rps=100))
        svc.score(HealthInput("ep2", availability_pct=50, error_rate_pct=10, throughput_rps=10, throughput_target_rps=100))
        summary = svc.get_summary()
        assert summary["total"] == 2
        assert summary["max_score"] > summary["min_score"]

    def test_empty_summary(self):
        svc = EndpointHealthScorer()
        assert svc.get_summary()["total"] == 0

    def test_zero_targets(self):
        svc = EndpointHealthScorer()
        result = svc.score(HealthInput("ep1", latency_target_ms=0, throughput_target_rps=0))
        assert result["components"]["latency"] == 100.0
        assert result["components"]["throughput"] == 100.0

    def test_isolation(self):
        a, b = EndpointHealthScorer(), EndpointHealthScorer()
        a.score(HealthInput("ep1"))
        assert b.get_score("ep1") is None
