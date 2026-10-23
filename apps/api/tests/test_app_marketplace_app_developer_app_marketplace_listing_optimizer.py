from app.services.app_marketplace_app_developer_app_marketplace_listing_optimizer import create_listing_experiment, evaluate_listing_experiment

def test_create():
    e = create_listing_experiment(app_id="a1", element="title", variants=["Title A", "Title B"])
    assert e["variant_count"] == 2

def test_invalid_element():
    e = create_listing_experiment(app_id="a1", element="color", variants=["A", "B"])
    assert e["error"]

def test_evaluate():
    data = [{"variant": "A", "conversion_rate": 5.5, "impressions": 1000},
            {"variant": "B", "conversion_rate": 7.2, "impressions": 1000}]
    r = evaluate_listing_experiment(variants_data=data)
    assert r["winner"] == "B"
    assert r["significant"]
