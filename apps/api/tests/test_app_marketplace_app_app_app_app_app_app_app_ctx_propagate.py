from app.services.app_marketplace_app_app_app_app_app_app_app_ctx_propagate import ContextPropagator

def test_propagate():
    cp = ContextPropagator()
    ctx = cp.create_context(user_id="u1", tenant_id="t1")
    assert ctx["request_id"].startswith("req-")
    assert ctx["trace_id"].startswith("trace-")
    cp.add_baggage(ctx["request_id"], "feature_flag", "dark_mode")
    extracted = cp.extract(ctx["request_id"])
    assert extracted["baggage"]["feature_flag"] == "dark_mode"
    cp.finish(ctx["request_id"])
    assert cp.stats()["active_contexts"] == 0
