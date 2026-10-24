from app.services.app_marketplace_app_app_app_app_app_app_app_sse_emitter import (
    emit_event, get_events, channel_stats, clear_channels,
)

def test_emit_get():
    clear_channels()
    emit_event("deploys", "deploy.started", {"version": "2.0"})
    emit_event("deploys", "deploy.completed", {"version": "2.0"})
    r = get_events("deploys")
    assert r["count"] == 2
    r2 = get_events("deploys", since_id=1)
    assert r2["count"] == 1
    clear_channels()

def test_stats():
    clear_channels()
    emit_event("a", "x", {})
    emit_event("b", "y", {})
    s = channel_stats()
    assert s["total_channels"] == 2
    assert s["total_events"] == 2
    clear_channels()
