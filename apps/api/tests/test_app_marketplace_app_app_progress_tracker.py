from app.services.app_marketplace_app_app_progress_tracker import build_progress

def test_progress():
    steps = [{"label": "Upload"}, {"label": "Process"}, {"label": "Review"}, {"label": "Publish"}]
    r = build_progress(steps=steps, current_step=2)
    assert r["total"] == 4
    assert r["steps"][0]["status"] == "completed"
    assert r["steps"][2]["status"] == "current"
    assert r["steps"][3]["status"] == "pending"
    assert r["progress_pct"] == 67

def test_complete():
    r = build_progress(steps=[{"label": "A"}, {"label": "B"}], current_step=1)
    assert r["is_complete"]
