"""Metrics counter isolation — different apps don't interfere."""

from app.services.app_metrics import increment, get_count, get_all_counts

def test_counters_isolated():
    increment("api_calls", "iso-app-1", 10)
    increment("api_calls", "iso-app-2", 20)
    assert get_count("api_calls", "iso-app-1") >= 10
    assert get_count("api_calls", "iso-app-2") >= 20

def test_different_metrics_isolated():
    increment("metric_a", "iso-app-3", 5)
    increment("metric_b", "iso-app-3", 15)
    assert get_count("metric_a", "iso-app-3") >= 5
    assert get_count("metric_b", "iso-app-3") >= 15

def test_get_all_includes_both():
    increment("x1", "iso-app-4", 1)
    increment("x2", "iso-app-4", 2)
    counts = get_all_counts("iso-app-4")
    assert "x1" in counts
    assert "x2" in counts

def test_unknown_app_zero():
    assert get_count("api_calls", "completely-unknown-app") == 0

def test_unknown_metric_zero():
    increment("known", "iso-app-5")
    assert get_count("unknown_metric_xyz", "iso-app-5") == 0
