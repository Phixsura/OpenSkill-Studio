"""Tests for App Health Score — signals, weights, grades."""

from app.services.app_health_score import AppHealthScore


class TestCompute:
    def test_perfect_health(self):
        h = AppHealthScore()
        r = h.compute(uptime_pct=100, error_rate_pct=0, avg_latency_ms=0, saturation_pct=0)
        assert r.overall_score == 100.0
        assert r.grade == "A"

    def test_degraded(self):
        h = AppHealthScore()
        r = h.compute(uptime_pct=99.5, error_rate_pct=3, avg_latency_ms=500, saturation_pct=80)
        assert r.grade in ("B", "C", "D")
        assert 0 < r.overall_score < 100

    def test_poor_health(self):
        h = AppHealthScore()
        r = h.compute(uptime_pct=90, error_rate_pct=10, avg_latency_ms=2000, saturation_pct=95)
        assert r.grade in ("D", "F")


class TestSignals:
    def test_signal_count(self):
        h = AppHealthScore()
        r = h.compute()
        assert len(r.signals) == 4

    def test_signal_names(self):
        h = AppHealthScore()
        r = h.compute()
        names = [s.name for s in r.signals]
        assert "uptime" in names
        assert "error_rate" in names
        assert "latency" in names
        assert "saturation" in names

    def test_signal_status(self):
        h = AppHealthScore()
        r = h.compute(uptime_pct=100, error_rate_pct=0)
        uptime = next(s for s in r.signals if s.name == "uptime")
        assert uptime.status == "ok"

    def test_degraded_status(self):
        h = AppHealthScore()
        r = h.compute(error_rate_pct=3)
        error = next(s for s in r.signals if s.name == "error_rate")
        assert error.status == "degraded"

    def test_critical_status(self):
        h = AppHealthScore()
        r = h.compute(error_rate_pct=10)
        error = next(s for s in r.signals if s.name == "error_rate")
        assert error.status == "critical"


class TestGrades:
    def test_a(self):
        h = AppHealthScore()
        assert h._grade(95) == "A"

    def test_b(self):
        h = AppHealthScore()
        assert h._grade(85) == "B"

    def test_f(self):
        h = AppHealthScore()
        assert h._grade(50) == "F"


class TestWeights:
    def test_custom_weights(self):
        h = AppHealthScore()
        r = h.compute(
            uptime_pct=100, error_rate_pct=0,
            weights={"uptime": 10, "error_rate": 0, "latency": 0, "saturation": 0},
        )
        assert r.overall_score == 100.0
