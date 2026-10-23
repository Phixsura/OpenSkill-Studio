from app.services.app_marketplace_app_app_loading_state import get_loading_state

def test_spinner():
    r = get_loading_state(variant="spinner")
    assert r["type"] == "spinner"
    assert r["message"] == "Loading..."

def test_progress():
    r = get_loading_state(variant="progress", message="Deploying...", progress_pct=65)
    assert r["show_progress"]
    assert r["progress_pct"] == 65
    assert r["message"] == "Deploying..."

def test_custom():
    r = get_loading_state(message="Fetching data...")
    assert r["message"] == "Fetching data..."
