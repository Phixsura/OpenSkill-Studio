"""App error tracker tests."""

import pytest
from app.services.app_error_tracker import record_error, get_errors, get_error_summary, get_top_errors, clear_errors

APP = "err-test-app"

@pytest.fixture(autouse=True)
def _clean():
    clear_errors(APP)
    yield
    clear_errors(APP)

def test_record_and_get():
    record_error(app_id=APP, error_type="TypeError", message="x is not a function")
    errors = get_errors(APP)
    assert len(errors) == 1
    assert errors[0]["error_type"] == "TypeError"

def test_summary():
    record_error(app_id=APP, error_type="TypeError", message="a")
    record_error(app_id=APP, error_type="TypeError", message="b")
    record_error(app_id=APP, error_type="ValueError", message="c")
    s = get_error_summary(APP)
    assert s["total"] == 3
    assert s["by_type"]["TypeError"] == 2
    assert s["unique_types"] == 2

def test_top_errors():
    for _ in range(5): record_error(app_id=APP, error_type="A", message="x")
    for _ in range(3): record_error(app_id=APP, error_type="B", message="x")
    for _ in range(1): record_error(app_id=APP, error_type="C", message="x")
    top = get_top_errors(APP, limit=2)
    assert top[0]["error_type"] == "A"
    assert top[0]["count"] == 5
    assert len(top) == 2

def test_clear():
    record_error(app_id=APP, error_type="X", message="x")
    count = clear_errors(APP)
    assert count == 1
    assert len(get_errors(APP)) == 0

def test_empty_app():
    assert get_errors("nonexistent") == []
    assert get_error_summary("nonexistent")["total"] == 0

def test_limit():
    for i in range(100): record_error(app_id=APP, error_type="E", message=f"m{i}")
    assert len(get_errors(APP, limit=10)) == 10
