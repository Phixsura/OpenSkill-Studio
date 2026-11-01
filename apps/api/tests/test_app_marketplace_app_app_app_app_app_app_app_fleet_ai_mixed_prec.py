from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_mixed_prec import fleet_ai_mixed_precision
def test_mp():
    r = fleet_ai_mixed_precision([{"active": True, "speedup_x": 2.5, "mem_reduction_pct": 50, "precisions": ["FP16", "BF16", "INT8"]}])
    assert r["speedup_x"] == 2.5
    assert r["optimized"]
