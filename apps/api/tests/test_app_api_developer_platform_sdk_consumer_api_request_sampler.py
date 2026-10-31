"""Tests for Endpoint Request Sampler service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_request_sampler import (
    RequestSampler, SamplingRule, SampledRequest,
)


class TestRequestSampler:
    def test_full_sample_rate(self):
        svc = RequestSampler()
        svc.set_rule(SamplingRule("r1", "ep1", 1.0))
        result = svc.evaluate(SampledRequest("req-1", "ep1", "GET", 200, 50.0))
        assert result["sampled"] is True

    def test_zero_sample_rate(self):
        svc = RequestSampler()
        svc.set_rule(SamplingRule("r1", "ep1", 0.0))
        result = svc.evaluate(SampledRequest("req-1", "ep1", "GET", 200, 50.0))
        assert result["sampled"] is False

    def test_deterministic_sampling(self):
        svc = RequestSampler()
        svc.set_rule(SamplingRule("r1", "ep1", 0.5))
        r1 = svc.should_sample("req-abc", "ep1")
        r2 = svc.should_sample("req-abc", "ep1")
        assert r1 == r2  # deterministic

    def test_no_rule(self):
        svc = RequestSampler()
        result = svc.evaluate(SampledRequest("req-1", "ep1", "GET", 200, 50.0))
        assert result["sampled"] is False
        assert result["reason"] == "no_rule"

    def test_condition_status_min(self):
        svc = RequestSampler()
        svc.set_rule(SamplingRule("r1", "ep1", 1.0, {"status_min": 400}))
        r1 = svc.evaluate(SampledRequest("req-1", "ep1", "GET", 200, 50.0))
        assert r1["sampled"] is False
        r2 = svc.evaluate(SampledRequest("req-2", "ep1", "GET", 500, 50.0))
        assert r2["sampled"] is True

    def test_condition_latency_min(self):
        svc = RequestSampler()
        svc.set_rule(SamplingRule("r1", "ep1", 1.0, {"latency_min_ms": 100}))
        r1 = svc.evaluate(SampledRequest("req-1", "ep1", "GET", 200, 50.0))
        assert r1["sampled"] is False
        r2 = svc.evaluate(SampledRequest("req-2", "ep1", "GET", 200, 150.0))
        assert r2["sampled"] is True

    def test_get_samples(self):
        svc = RequestSampler()
        svc.set_rule(SamplingRule("r1", "ep1", 1.0))
        svc.evaluate(SampledRequest("r1", "ep1", "GET", 200, 50.0))
        svc.evaluate(SampledRequest("r2", "ep1", "POST", 201, 80.0))
        samples = svc.get_samples()
        assert len(samples) == 2

    def test_stats(self):
        svc = RequestSampler()
        svc.set_rule(SamplingRule("r1", "ep1", 1.0))
        svc.evaluate(SampledRequest("r1", "ep1", "GET", 200, 50.0))
        stats = svc.get_stats()
        assert stats["total_evaluated"] == 1
        assert stats["total_sampled"] == 1

    def test_invalid_rate(self):
        svc = RequestSampler()
        with pytest.raises(ValueError):
            svc.set_rule(SamplingRule("r1", "ep1", 1.5))

    def test_remove_rule(self):
        svc = RequestSampler()
        svc.set_rule(SamplingRule("r1", "ep1", 0.5))
        assert svc.remove_rule("ep1")["removed"] is True
        assert svc.list_rules() == []

    def test_isolation(self):
        a, b = RequestSampler(), RequestSampler()
        a.set_rule(SamplingRule("r1", "ep1", 1.0))
        assert b.evaluate(SampledRequest("r1", "ep1", "GET", 200, 50))["reason"] == "no_rule"
