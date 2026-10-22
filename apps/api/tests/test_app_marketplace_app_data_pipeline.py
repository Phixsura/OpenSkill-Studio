from app.services.app_marketplace_app_data_pipeline import create_pipeline, execute_pipeline_step, get_pipeline_stats

def test_create():
    p = create_pipeline(app_id="a1", name="sync", source={"type": "webhook"},
                         transforms=[{"type": "filter"}], destination={"type": "db"})
    assert p["status"] == "created"
    assert p["transform_count"] == 1

def test_no_source():
    p = create_pipeline(app_id="a1", name="x", source={}, transforms=[], destination={})
    assert p["error"]

def test_filter():
    data = [{"status": "active", "name": "A"}, {"status": "inactive", "name": "B"}]
    r = execute_pipeline_step(step={"type": "filter", "field": "status", "value": "active"}, data=data)
    assert len(r) == 1

def test_aggregate():
    data = [{"score": 10}, {"score": 20}, {"score": 30}]
    r = execute_pipeline_step(step={"type": "aggregate", "field": "score"}, data=data)
    assert r[0]["sum"] == 60
    assert r[0]["avg"] == 20

def test_stats():
    runs = [{"status": "success", "duration_ms": 100}, {"status": "failed", "duration_ms": 200}]
    s = get_pipeline_stats(runs=runs)
    assert s["success_rate"] == 50.0
