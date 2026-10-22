from app.services.app_marketplace_app_funnel_analytics import build_funnel, compare_funnels

def test_funnel():
    f = build_funnel(page_views=10000, detail_views=3000, install_starts=500, install_completes=200)
    assert f["overall_conversion"] == 2.0
    assert f["steps"][0]["conversion_pct"] == 100.0
    assert f["steps"][1]["conversion_pct"] == 30.0

def test_compare():
    a = build_funnel(page_views=1000, detail_views=300, install_starts=50, install_completes=20)
    b = build_funnel(page_views=1000, detail_views=400, install_starts=80, install_completes=40)
    c = compare_funnels(funnel_a=a, funnel_b=b)
    assert c["overall_diff"] > 0
    assert c["comparison"][1]["b_conversion"] > c["comparison"][1]["a_conversion"]
