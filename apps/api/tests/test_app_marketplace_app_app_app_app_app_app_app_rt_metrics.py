from app.services.app_marketplace_app_app_app_app_app_app_app_rt_metrics import (
    emit_metric, get_stream, stream_stats, clear_streams,
)

def test_stream():
    clear_streams()
    emit_metric("cpu", "cpu_pct", 45.0, {"host": "node-1"})
    emit_metric("cpu", "cpu_pct", 52.0)
    emit_metric("cpu", "cpu_pct", 48.0)
    r = get_stream("cpu")
    assert r["count"] == 3
    assert r["latest"] == 48.0
    assert r["avg"] == 48.33
    clear_streams()

def test_stats():
    clear_streams()
    emit_metric("a", "x", 1)
    emit_metric("b", "y", 2)
    s = stream_stats()
    assert s["total_streams"] == 2
    assert s["total_points"] == 2
    clear_streams()
