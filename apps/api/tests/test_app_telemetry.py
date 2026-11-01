"""App telemetry tests."""
import pytest
from app.services.app_telemetry import record_event, get_performance_summary, clear_telemetry

APP = "telem-test"

@pytest.fixture(autouse=True)
def _clean():
    clear_telemetry(APP)
    yield
    clear_telemetry(APP)

def test_record_and_summary():
    for d in [100, 200, 300, 400, 500]:
        record_event(APP, "exec", duration_ms=d)
    s = get_performance_summary(APP)
    assert s["count"] == 5
    assert s["avg_ms"] == 300.0

def test_empty_summary():
    s = get_performance_summary("no-events")
    assert s["count"] == 0
    assert s["avg_ms"] == 0

def test_percentiles():
    for i in range(100):
        record_event(APP, "exec", duration_ms=i + 1)
    s = get_performance_summary(APP)
    assert s["p50_ms"] == 51
    assert s["p95_ms"] >= 90

def test_clear():
    record_event(APP, "x", duration_ms=10)
    count = clear_telemetry(APP)
    assert count == 1
    assert get_performance_summary(APP)["count"] == 0
