"""Tests for App Traffic Mirror — rules, mirroring, divergence."""

import pytest

from app.services.app_traffic_mirror import AppTrafficMirror


class TestAddRule:
    def test_add(self):
        m = AppTrafficMirror()
        r = m.add_rule("inst-1", "r1", "/api/users", "https://shadow.example.com/api/users")
        assert r.source_path == "/api/users"
        assert r.enabled is True
        assert r.sample_rate == 1.0

    def test_custom_sample_rate(self):
        m = AppTrafficMirror()
        r = m.add_rule("inst-1", "r1", "/api", "https://shadow.com", sample_rate=0.1)
        assert r.sample_rate == 0.1

    def test_invalid_sample_rate(self):
        m = AppTrafficMirror()
        with pytest.raises(ValueError, match="sample_rate"):
            m.add_rule("inst-1", "r1", "/api", "https://x.com", sample_rate=0)

    def test_duplicate(self):
        m = AppTrafficMirror()
        m.add_rule("inst-1", "r1", "/api", "https://x.com")
        with pytest.raises(ValueError, match="already exists"):
            m.add_rule("inst-1", "r1", "/other", "https://y.com")


class TestMirror:
    def test_record(self):
        m = AppTrafficMirror()
        m.add_rule("inst-1", "r1", "/api", "https://x.com")
        r = m.record_mirror("inst-1", "r1")
        assert r.mirrored_count == 1

    def test_divergence(self):
        m = AppTrafficMirror()
        m.add_rule("inst-1", "r1", "/api", "https://x.com")
        m.record_mirror("inst-1", "r1", diverged=True)
        assert m._get("inst-1", "r1").divergence_count == 1


class TestDivergenceRate:
    def test_rate(self):
        m = AppTrafficMirror()
        m.add_rule("inst-1", "r1", "/api", "https://x.com")
        for _ in range(8):
            m.record_mirror("inst-1", "r1")
        for _ in range(2):
            m.record_mirror("inst-1", "r1", diverged=True)
        assert m.get_divergence_rate("inst-1", "r1") == 20.0

    def test_zero_mirrors(self):
        m = AppTrafficMirror()
        m.add_rule("inst-1", "r1", "/api", "https://x.com")
        assert m.get_divergence_rate("inst-1", "r1") == 0.0


class TestEnableDisable:
    def test_disable(self):
        m = AppTrafficMirror()
        m.add_rule("inst-1", "r1", "/api", "https://x.com")
        r = m.disable_rule("inst-1", "r1")
        assert r.enabled is False

    def test_enable(self):
        m = AppTrafficMirror()
        m.add_rule("inst-1", "r1", "/api", "https://x.com")
        m.disable_rule("inst-1", "r1")
        r = m.enable_rule("inst-1", "r1")
        assert r.enabled is True


class TestIsolation:
    def test_cross_installation(self):
        m = AppTrafficMirror()
        m.add_rule("inst-1", "r1", "/api", "https://x.com")
        with pytest.raises(KeyError):
            m._get("inst-2", "r1")
