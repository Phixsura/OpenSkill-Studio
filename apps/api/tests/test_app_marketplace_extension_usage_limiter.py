from app.services.app_marketplace_extension_usage_limiter import UsageLimiter


def test_no_limit():
    ul = UsageLimiter()
    result = ul.check("ext-1", "org-1", "api_calls")
    assert result["allowed"] is True
    assert result["reason"] == "no_limit"


def test_within_limits():
    ul = UsageLimiter()
    ul.configure("ext-2", "org-1", "api_calls", 60.0, hard_limit=100, soft_limit=80)
    for _ in range(50):
        ul.record("ext-2", "org-1", "api_calls")
    status = ul.check("ext-2", "org-1", "api_calls")
    assert status["allowed"] is True
    assert status["warning"] is False


def test_soft_limit_warning():
    ul = UsageLimiter()
    ul.configure("ext-3", "org-1", "api_calls", 60.0, hard_limit=100, soft_limit=10)
    for _ in range(15):
        ul.record("ext-3", "org-1", "api_calls")
    status = ul.check("ext-3", "org-1", "api_calls")
    assert status["allowed"] is True
    assert status["warning"] is True


def test_hard_limit_blocks():
    ul = UsageLimiter()
    ul.configure("ext-4", "org-1", "api_calls", 60.0, hard_limit=5, soft_limit=3)
    for _ in range(5):
        ul.record("ext-4", "org-1", "api_calls")
    result = ul.record("ext-4", "org-1", "api_calls")
    assert result["limited"] is True
    assert result["recorded"] is False


def test_get_usage():
    ul = UsageLimiter()
    ul.configure("ext-5", "org-1", "api_calls", 60.0, 100, 80)
    ul.configure("ext-5", "org-1", "storage", 3600.0, 500, 400)
    ul.record("ext-5", "org-1", "api_calls")
    usage = ul.get_usage("ext-5", "org-1")
    assert "api_calls" in usage["metrics"]
    assert "storage" in usage["metrics"]
    assert usage["metrics"]["api_calls"]["current"] == 1


def test_reset():
    ul = UsageLimiter()
    ul.configure("ext-6", "org-1", "ops", 60.0, 10, 5)
    for _ in range(5):
        ul.record("ext-6", "org-1", "ops")
    ul.reset("ext-6", "org-1", "ops")
    status = ul.check("ext-6", "org-1", "ops")
    assert status["current"] == 0
