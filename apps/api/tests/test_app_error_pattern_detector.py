from app.services.app_error_pattern_detector import detect_patterns, is_new_error

ERRORS = [{"error_type": "TypeError", "message": "x"} for _ in range(5)] + [{"error_type": "ValueError", "message": "y"}]

def test_detect():
    p = detect_patterns(ERRORS, min_occurrences=3)
    assert len(p) == 1
    assert p[0]["type"] == "TypeError"

def test_is_new():
    patterns = [{"type": "TypeError", "count": 5}]
    assert is_new_error("ValueError", patterns) is True
    assert is_new_error("TypeError", patterns) is False

def test_empty():
    assert detect_patterns([]) == []
