from app.services.app_marketplace_app_app_app_app_app_app_app_data_pipeline import create_pipeline, run_pipeline

def test_pipeline():
    p = create_pipeline("user_etl", [
        {"name": "active_only", "action": "filter", "field": "status", "value": "active"},
        {"name": "sort_name", "action": "sort", "field": "name"},
    ])
    assert p["step_count"] == 2
    data = [
        {"name": "Charlie", "status": "active"},
        {"name": "Alice", "status": "active"},
        {"name": "Bob", "status": "inactive"},
    ]
    r = run_pipeline(p, data)
    assert r["input_count"] == 3
    assert r["output_count"] == 2
    assert r["output"][0]["name"] == "Alice"
    assert r["status"] == "completed"
