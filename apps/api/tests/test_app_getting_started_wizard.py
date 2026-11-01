from app.services.app_getting_started_wizard import get_wizard_steps, get_wizard_progress

def test_steps():
    assert len(get_wizard_steps()) == 5

def test_progress_start():
    p = get_wizard_progress(set())
    assert p["done"] == 0
    assert p["current_step"]["id"] == "choose_template"

def test_progress_mid():
    p = get_wizard_progress({"choose_template", "basic_info"})
    assert p["done"] == 2
    assert p["pct"] == 40

def test_progress_done():
    all_ids = {s["id"] for s in get_wizard_steps()}
    p = get_wizard_progress(all_ids)
    assert p["done"] == 5
    assert p["current_step"] is None
