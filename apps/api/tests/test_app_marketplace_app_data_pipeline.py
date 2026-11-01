from app.services.app_marketplace_app_data_pipeline import create_pipeline, estimate_pipeline_cost

def test_create():
    r = create_pipeline(name="Analytics ETL",
        source={"type": "postgres", "table": "events"},
        transforms=[{"type": "filter", "condition": "type = 'click'"}],
        destination={"type": "bigquery", "dataset": "analytics"},
        schedule="0 3 * * *")
    assert r["pipeline_id"].startswith("dp_")
    assert r["status"] == "active"
    assert r["transforms"][0]["step"] == 1

def test_no_source():
    r = create_pipeline(name="X", source={}, transforms=[], destination={"type": "s3"})
    assert "error" in r

def test_cost():
    r = estimate_pipeline_cost(rows_per_day=10_000_000, transforms=3, storage_gb=50)
    assert r["total_daily"] > 0
    assert r["estimated_monthly"] == round(r["total_daily"] * 30, 2)
