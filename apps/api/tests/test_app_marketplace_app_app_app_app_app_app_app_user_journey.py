from app.services.app_marketplace_app_app_app_app_app_app_app_user_journey import build_funnel, identify_bottleneck

def test_funnel():
    r = build_funnel(["Visit", "Signup", "Activate", "Subscribe"],
                       [1000, 500, 200, 50])
    assert r["overall_conversion"] == 5.0
    assert r["funnel"][1]["drop_off"] == 500
    assert r["funnel"][1]["drop_off_pct"] == 50.0

def test_bottleneck():
    funnel = build_funnel(["A", "B", "C"], [100, 30, 25])
    r = identify_bottleneck(funnel)
    assert r["bottleneck"] == "B"  # 70% drop
