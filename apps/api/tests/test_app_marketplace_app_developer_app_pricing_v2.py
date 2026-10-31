from app.services.app_marketplace_app_developer_app_pricing_v2 import create_pricing_model, calculate_price

def test_create():
    m = create_pricing_model(model_type="usage_based", per_unit_price_cents=1)
    assert m["model_type"] == "usage_based"

def test_invalid():
    m = create_pricing_model(model_type="auction")
    assert m["error"]

def test_free():
    m = {"model_type": "free"}
    r = calculate_price(model=m, usage=1000)
    assert r["total_cents"] == 0

def test_usage():
    m = {"model_type": "usage_based", "per_unit_price_cents": 1}
    r = calculate_price(model=m, usage=5000)
    assert r["total_cents"] == 5000

def test_tiered():
    m = {"model_type": "tiered", "tiers": [
        {"name": "free", "up_to": 1000, "per_unit_cents": 0},
        {"name": "standard", "up_to": 10000, "per_unit_cents": 1},
    ]}
    r = calculate_price(model=m, usage=5000)
    assert r["total_cents"] == 4000  # 1000 free + 4000 * 1
