from app.services.app_marketplace_app_app_error_boundary import capture_error, build_error_summary

def test_capture_exception():
    try:
        raise ValueError("bad input")
    except Exception as e:
        r = capture_error(error=e, context={"user": "u1"})
    assert r["type"] == "ValueError"
    assert "bad input" in r["message"]
    assert r["stack"] is not None
    assert r["context"]["user"] == "u1"

def test_capture_string():
    r = capture_error(error="Something went wrong")
    assert r["type"] == "Error"
    assert r["stack"] is None

def test_summary():
    e1 = capture_error(error="oops")
    e2 = capture_error(error="oops")
    e3 = capture_error(error="different error")
    r = build_error_summary(errors=[e1, e2, e3])
    assert r["total_errors"] == 3
    assert r["unique_errors"] == 2
    assert r["groups"][0]["count"] == 2
