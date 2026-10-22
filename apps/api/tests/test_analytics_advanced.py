"""Advanced analytics service tests."""

from app.services.app_analytics import (
    get_app_summary_metrics,
    get_execution_timeline,
    get_install_timeline,
    get_top_orgs,
)
from app.services.app_metrics import (
    METRIC_API_CALLS,
    METRIC_INSTALLS,
    METRIC_SANDBOX_EXECUTIONS,
    METRIC_WEBHOOK_DELIVERIES,
    get_all_counts,
    increment,
)


def test_analytics_functions_async():
    import asyncio
    assert asyncio.iscoroutinefunction(get_install_timeline)
    assert asyncio.iscoroutinefunction(get_execution_timeline)
    assert asyncio.iscoroutinefunction(get_top_orgs)
    assert asyncio.iscoroutinefunction(get_app_summary_metrics)


def test_metrics_increment_large():
    increment("large_test", "app-large", 100)
    from app.services.app_metrics import get_count
    assert get_count("large_test", "app-large") >= 100


def test_metrics_all_predefined():
    expected = [METRIC_API_CALLS, METRIC_INSTALLS, METRIC_SANDBOX_EXECUTIONS, METRIC_WEBHOOK_DELIVERIES]
    for m in expected:
        assert isinstance(m, str)
        assert len(m) > 0


def test_metrics_get_all_empty():
    counts = get_all_counts("totally-new-app")
    assert isinstance(counts, dict)


def test_metrics_increment_zero():
    increment("zero_test", "app-zero", 0)
    from app.services.app_metrics import get_count
    # Should not error
    assert get_count("zero_test", "app-zero") >= 0
