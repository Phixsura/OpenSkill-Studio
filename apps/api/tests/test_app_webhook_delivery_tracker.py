from app.services.app_webhook_delivery_tracker import track_attempt, get_delivery_attempts, get_delivery_outcome, clear_tracker

def setup_function():
    clear_tracker()

def test_track():
    track_attempt(delivery_id="d1", app_id="a1", attempt=1, status_code=500, duration_ms=100, success=False)
    assert len(get_delivery_attempts("d1")) == 1

def test_outcome_delivered():
    track_attempt(delivery_id="d2", app_id="a1", attempt=1, status_code=500, duration_ms=100, success=False)
    track_attempt(delivery_id="d2", app_id="a1", attempt=2, status_code=200, duration_ms=50, success=True)
    assert get_delivery_outcome("d2") == "delivered"

def test_outcome_failed():
    track_attempt(delivery_id="d3", app_id="a1", attempt=1, status_code=500, duration_ms=100, success=False)
    assert get_delivery_outcome("d3") == "failed"

def test_outcome_pending():
    assert get_delivery_outcome("unknown") == "pending"

def test_clear():
    track_attempt(delivery_id="d4", app_id="a1", attempt=1, status_code=200, duration_ms=50, success=True)
    count = clear_tracker()
    assert count >= 1
