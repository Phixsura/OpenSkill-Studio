from app.services.app_event_deduplicator import is_duplicate, mark_processed, clear

def setup_function():
    clear()

def test_first_not_duplicate():
    assert is_duplicate("evt_1") is False

def test_second_is_duplicate():
    is_duplicate("evt_2")
    assert is_duplicate("evt_2") is True

def test_mark_processed():
    mark_processed("evt_3")
    assert is_duplicate("evt_3") is True

def test_different_ids():
    is_duplicate("evt_a")
    assert is_duplicate("evt_b") is False

def test_clear():
    is_duplicate("evt_x")
    count = clear()
    assert count >= 1
    assert is_duplicate("evt_x") is False  # cleared

def test_capacity():
    for i in range(100):
        is_duplicate(f"cap_{i}")
    # All should be tracked
    assert is_duplicate("cap_99") is True
