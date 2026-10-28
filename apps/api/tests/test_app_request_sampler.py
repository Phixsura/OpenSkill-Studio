"""Tests for App Request Sampler — sampling, storage, queries."""

import pytest

from app.services.app_request_sampler import AppRequestSampler, SampledRequest


class TestShouldSample:
    def test_deterministic(self):
        s = AppRequestSampler(sample_rate=0.5)
        r1 = s.should_sample("req-123")
        r2 = s.should_sample("req-123")
        assert r1 == r2

    def test_rate_respected(self):
        s = AppRequestSampler(sample_rate=0.5)
        sampled = sum(1 for i in range(1000) if s.should_sample(f"req-{i}"))
        assert 350 < sampled < 650  # roughly 50% ± margin

    def test_invalid_rate(self):
        with pytest.raises(ValueError):
            AppRequestSampler(sample_rate=0)


class TestStoreSample:
    def test_store(self):
        s = AppRequestSampler()
        sample = SampledRequest(sample_id="s1", method="GET", path="/api/users", status_code=200)
        s.store_sample("inst-1", sample)
        assert s.sample_count("inst-1") == 1

    def test_max_limit(self):
        s = AppRequestSampler(max_samples=5)
        for i in range(10):
            s.store_sample("inst-1", SampledRequest(sample_id=f"s{i}", method="GET", path="/api", status_code=200))
        assert s.sample_count("inst-1") == 5


class TestGetSamples:
    def test_newest_first(self):
        s = AppRequestSampler()
        s.store_sample("inst-1", SampledRequest(sample_id="s1", method="GET", path="/a", status_code=200))
        s.store_sample("inst-1", SampledRequest(sample_id="s2", method="GET", path="/b", status_code=200))
        samples = s.get_samples("inst-1")
        assert samples[0].sample_id == "s2"

    def test_filter_method(self):
        s = AppRequestSampler()
        s.store_sample("inst-1", SampledRequest(sample_id="s1", method="GET", path="/a", status_code=200))
        s.store_sample("inst-1", SampledRequest(sample_id="s2", method="POST", path="/a", status_code=201))
        assert len(s.get_samples("inst-1", method="GET")) == 1

    def test_filter_status(self):
        s = AppRequestSampler()
        s.store_sample("inst-1", SampledRequest(sample_id="s1", method="GET", path="/a", status_code=200))
        s.store_sample("inst-1", SampledRequest(sample_id="s2", method="GET", path="/b", status_code=500))
        errors = s.get_samples("inst-1", status_min=400)
        assert len(errors) == 1


class TestIsolation:
    def test_cross_installation(self):
        s = AppRequestSampler()
        s.store_sample("inst-1", SampledRequest(sample_id="s1", method="GET", path="/a", status_code=200))
        assert s.sample_count("inst-2") == 0
