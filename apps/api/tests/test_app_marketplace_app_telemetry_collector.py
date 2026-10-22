from app.services.app_marketplace_app_telemetry_collector import collect_telemetry_event, aggregate_telemetry, build_telemetry_funnel

def test_collect():
    e = collect_telemetry_event(app_id="a1", event_name="page_view", properties={"page": "/home"}, session_id="s1")
    assert e["event_name"] == "page_view"

def test_aggregate():
    events = [{"event_name": "view", "session_id": "s1"}, {"event_name": "view", "session_id": "s1"},
              {"event_name": "click", "session_id": "s2"}]
    r = aggregate_telemetry(events=events)
    assert r["total_events"] == 3
    assert r["unique_sessions"] == 2
    assert r["event_counts"]["view"] == 2

def test_funnel():
    events = [{"event_name": "view"}] * 100 + [{"event_name": "click"}] * 30 + [{"event_name": "install"}] * 10
    f = build_telemetry_funnel(events=events, funnel_steps=["view", "click", "install"])
    assert f["steps"][0]["count"] == 100
    assert f["steps"][1]["conversion_pct"] == 30.0
    assert f["overall_pct"] == 10.0
