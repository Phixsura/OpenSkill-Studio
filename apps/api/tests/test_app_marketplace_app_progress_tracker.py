from app.services.app_marketplace_app_progress_tracker import create_progress

def test_in_progress():
    steps = [
        {"name": "Setup", "status": "completed"},
        {"name": "Configure", "status": "in_progress"},
        {"name": "Deploy", "status": "pending"},
    ]
    r = create_progress(title="App Setup", steps=steps)
    assert r["progress_pct"] == 33
    assert r["current_step"] == 1
    assert not r["all_complete"]

def test_complete():
    steps = [{"name": "A", "status": "completed"}, {"name": "B", "status": "completed"}]
    r = create_progress(title="Done", steps=steps)
    assert r["all_complete"]
    assert r["progress_pct"] == 100
