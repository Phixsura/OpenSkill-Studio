from app.services.app_marketplace_app_app_app_app_app_app_app_tour_guide import get_tour, track_progress, list_tours

def test_tour():
    t = get_tour("getting_started")
    assert t["total_steps"] == 5
    assert t["steps"][0]["title"] == "Welcome to OpenSkill!"

def test_progress():
    p = track_progress("getting_started", ["welcome", "create_app"])
    assert p["completed"] == 2
    assert p["progress_pct"] == 40
    assert p["next_step"] == "api_key"
    assert not p["finished"]

def test_list():
    tours = list_tours()
    assert len(tours) == 2
