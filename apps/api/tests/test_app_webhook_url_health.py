from app.services.app_webhook_url_health import record_check, get_url_health, list_unhealthy_urls

def test_record_healthy():
    record_check("https://good.com/hook", reachable=True, status_code=200, latency_ms=50)
    h = get_url_health("https://good.com/hook")
    assert h is not None and h["healthy"] is True

def test_record_unreachable():
    record_check("https://down.com/hook", reachable=False)
    h = get_url_health("https://down.com/hook")
    assert h["healthy"] is False

def test_record_500():
    record_check("https://err.com/hook", reachable=True, status_code=500)
    h = get_url_health("https://err.com/hook")
    assert h["healthy"] is False

def test_unknown_url():
    assert get_url_health("https://never-checked.com") is None

def test_unhealthy_list():
    record_check("https://bad1.com", reachable=False)
    unhealthy = list_unhealthy_urls()
    assert any(u["url"] == "https://bad1.com" for u in unhealthy)
