from app.services.app_marketplace_app_app_app_app_app_app_app_rl_dash_agg import aggregate_rate_limits

def test_aggregate():
    r = aggregate_rate_limits([
        {"key": "u1", "allowed": True}, {"key": "u1", "allowed": True},
        {"key": "u1", "allowed": False}, {"key": "u2", "allowed": False},
        {"key": "u2", "allowed": False},
    ])
    assert r["total_events"] == 5
    assert r["total_denied"] == 3
    assert r["keys"][0]["key"] == "u2"  # most denied first
    assert r["keys"][0]["deny_rate"] == 100.0
