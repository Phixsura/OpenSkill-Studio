from app.services.app_marketplace_extension_quota_enforcer import QuotaEnforcerService


def test_basic_consume():
    qe = QuotaEnforcerService()
    qe.configure("t1", "api_calls", 100, unit="calls")
    r = qe.check_and_consume("t1", "api_calls", 10)
    assert r.allowed is True
    assert r.used == 10
    assert r.remaining == 90


def test_exceed_hard_limit():
    qe = QuotaEnforcerService()
    qe.configure("t1", "storage", 100, unit="MB")
    qe.check_and_consume("t1", "storage", 90)
    r = qe.check_and_consume("t1", "storage", 20)
    assert r.allowed is False
    assert r.status == "exceeded"


def test_soft_limit_warning():
    qe = QuotaEnforcerService()
    qe.configure("t1", "bandwidth", 100, soft_limit=80)
    qe.check_and_consume("t1", "bandwidth", 85)
    r = qe.check_and_consume("t1", "bandwidth", 1)
    assert r.allowed is True
    assert r.status == "warning"


def test_grace_period():
    qe = QuotaEnforcerService()
    qe.configure("t1", "api_calls", 10, grace_seconds=60)
    qe.check_and_consume("t1", "api_calls", 10)
    r = qe.check_and_consume("t1", "api_calls", 1)  # over limit but in grace
    assert r.allowed is True
    assert r.status == "grace"


def test_no_quota_configured():
    qe = QuotaEnforcerService()
    r = qe.check_and_consume("t1", "unknown")
    assert r.allowed is True
    assert r.status == "no_quota"


def test_reset():
    qe = QuotaEnforcerService()
    qe.configure("t1", "calls", 100)
    qe.check_and_consume("t1", "calls", 50)
    qe.reset("t1", "calls")
    usage = qe.get_usage("t1")
    assert usage["calls"]["used"] == 0


def test_reset_all():
    qe = QuotaEnforcerService()
    qe.configure("t1", "a", 100)
    qe.configure("t1", "b", 200)
    qe.check_and_consume("t1", "a", 50)
    qe.check_and_consume("t1", "b", 100)
    qe.reset("t1")
    usage = qe.get_usage("t1")
    assert usage["a"]["used"] == 0
    assert usage["b"]["used"] == 0


def test_usage_report():
    qe = QuotaEnforcerService()
    qe.configure("t1", "storage", 1000, soft_limit=800, unit="MB")
    qe.check_and_consume("t1", "storage", 500)
    usage = qe.get_usage("t1")
    assert usage["storage"]["pct"] == 50.0
    assert usage["storage"]["status"] == "ok"


def test_top_consumers():
    qe = QuotaEnforcerService()
    qe.configure("t1", "api", 1000); qe.check_and_consume("t1", "api", 500)
    qe.configure("t2", "api", 1000); qe.check_and_consume("t2", "api", 800)
    qe.configure("t3", "api", 1000); qe.check_and_consume("t3", "api", 200)
    top = qe.top_consumers("api", 2)
    assert top[0] == ("t2", 800)
    assert len(top) == 2


def test_default_soft_limit():
    qe = QuotaEnforcerService()
    qe.configure("t1", "x", 100)  # soft_limit auto = 80
    qe.check_and_consume("t1", "x", 81)
    r = qe.check_and_consume("t1", "x", 1)
    assert r.status == "warning"
