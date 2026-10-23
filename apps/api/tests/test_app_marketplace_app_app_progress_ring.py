from app.services.app_marketplace_app_app_progress_ring import calculate_ring

def test_full():
    r = calculate_ring(value=100, max_value=100, label="Completion")
    assert r["percentage"] == 100
    assert r["offset"] == 0
    assert r["color"] == "green"

def test_half():
    r = calculate_ring(value=50, max_value=100)
    assert r["percentage"] == 50
    assert r["color"] == "blue"

def test_low():
    r = calculate_ring(value=10, max_value=100)
    assert r["color"] == "red"
