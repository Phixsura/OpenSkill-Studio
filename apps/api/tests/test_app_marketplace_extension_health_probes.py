from app.services.app_marketplace_extension_health_probes import HealthProbeService


def test_liveness_healthy():
    hp = HealthProbeService()
    hp.add_liveness_check("process", lambda: (True, "running"))
    result = hp.liveness()
    assert result.status == "ok"
    assert result.http_status == 200


def test_liveness_unhealthy():
    hp = HealthProbeService()
    count = [0]
    def check():
        count[0] += 1
        return (False, "deadlocked")
    hp.add_liveness_check("process", check, failure_threshold=2)
    hp.liveness()  # 1st failure
    hp.liveness()  # 2nd failure → threshold
    result = hp.liveness()
    assert result.status == "fail"
    assert result.http_status == 503


def test_readiness_healthy():
    hp = HealthProbeService()
    hp.mark_started()
    hp.add_readiness_check("db", lambda: (True, "connected"))
    hp.add_readiness_check("cache", lambda: (True, "connected"))
    result = hp.readiness()
    assert result.status == "ok"


def test_readiness_one_failing():
    hp = HealthProbeService()
    hp.mark_started()
    hp.add_readiness_check("db", lambda: (True, "ok"))
    hp.add_readiness_check("cache", lambda: (False, "connection refused"))
    result = hp.readiness()
    assert result.status == "fail"
    assert result.checks["cache"]["healthy"] is False


def test_startup_blocks_readiness():
    hp = HealthProbeService()
    hp.add_startup_check("init", lambda: (False, "loading"))
    hp.add_readiness_check("db", lambda: (True, "ok"))
    result = hp.readiness()
    assert result.status == "fail"  # startup not complete


def test_startup_completes():
    hp = HealthProbeService()
    hp.add_startup_check("init", lambda: (True, "loaded"))
    result = hp.startup()
    assert result.status == "ok"
    assert hp.is_started() is True
    # Now readiness works
    hp.add_readiness_check("db", lambda: (True, "ok"))
    assert hp.readiness().status == "ok"


def test_threshold_recovery():
    hp = HealthProbeService()
    calls = [0]
    def flaky():
        calls[0] += 1
        return (calls[0] > 3, "recovering" if calls[0] > 3 else "failing")
    hp.add_liveness_check("svc", flaky, failure_threshold=5)
    for _ in range(3):
        hp.liveness()
    # Now starts succeeding
    hp.liveness()  # success resets consecutive_failures
    result = hp.liveness()
    assert result.status == "ok"


def test_exception_in_check():
    hp = HealthProbeService()
    hp.add_liveness_check("bad", lambda: (_ for _ in ()).throw(RuntimeError("crash")))
    result = hp.liveness()
    assert result.checks["bad"]["healthy"] is False
    assert "crash" in result.checks["bad"]["message"]


def test_no_checks():
    hp = HealthProbeService()
    assert hp.liveness().status == "ok"
    assert hp.readiness().status == "ok"
    assert hp.startup().status == "ok"


def test_get_all():
    hp = HealthProbeService()
    hp.add_liveness_check("proc", lambda: (True, "ok"))
    hp.mark_started()
    all_probes = hp.get_all()
    assert "liveness" in all_probes
    assert "readiness" in all_probes
    assert all_probes["started"] is True
