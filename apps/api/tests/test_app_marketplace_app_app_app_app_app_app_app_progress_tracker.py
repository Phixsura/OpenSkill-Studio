from app.services.app_marketplace_app_app_app_app_app_app_app_progress_tracker import create_progress, complete_step, get_next_step

def test_progress():
    p = create_progress(title="Setup", steps=["Create", "Configure", "Deploy", "Verify"])
    assert p["total"] == 4
    assert p["pct"] == 0
    complete_step(p, 0)
    complete_step(p, 1)
    assert p["pct"] == 50
    assert get_next_step(p)["label"] == "Deploy"
    complete_step(p, 2)
    r = complete_step(p, 3)
    assert r["finished"]
    assert p["pct"] == 100
    assert get_next_step(p) is None
