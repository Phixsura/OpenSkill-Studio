from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_trace_ctx import fleet_trace_context
def test_ctx():
    r = fleet_trace_context([{"propagates_context": True}, {"propagates_context": True}, {"propagates_context": False}])
    assert r["coverage_pct"] == 66.7
    assert not r["complete"]
