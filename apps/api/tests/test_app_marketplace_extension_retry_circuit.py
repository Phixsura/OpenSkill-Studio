from app.services.app_marketplace_extension_retry_circuit import (
    RetryCircuitService, RetryCircuitConfig
)


def test_success():
    rc = RetryCircuitService()
    rc.register("api")
    result = rc.call("api", lambda: 42)
    assert result.success is True
    assert result.result == 42
    assert result.attempts == 1


def test_retry_then_succeed():
    rc = RetryCircuitService()
    rc.register("api", RetryCircuitConfig(max_retries=3))
    count = [0]
    def flaky():
        count[0] += 1
        if count[0] < 3:
            raise RuntimeError("fail")
        return "ok"
    result = rc.call("api", flaky)
    assert result.success is True
    assert result.attempts == 3


def test_all_retries_fail():
    rc = RetryCircuitService()
    rc.register("api", RetryCircuitConfig(max_retries=2))
    result = rc.call("api", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    assert result.success is False
    assert result.attempts == 2
    assert "boom" in result.error


def test_circuit_opens():
    rc = RetryCircuitService()
    rc.register("api", RetryCircuitConfig(max_retries=1, failure_threshold=3))
    def fail():
        raise RuntimeError("err")
    for _ in range(3):
        rc.call("api", fail)
    state = rc.get_state("api")
    assert state["state"] == "open"


def test_circuit_open_rejects():
    rc = RetryCircuitService()
    rc.register("api", RetryCircuitConfig(max_retries=1, failure_threshold=2,
                                           recovery_timeout_s=999))
    def fail(): raise RuntimeError("err")
    rc.call("api", fail)
    rc.call("api", fail)  # opens circuit
    result = rc.call("api", lambda: "should not run")
    assert result.success is False
    assert result.circuit_state == "open"


def test_half_open_recovery():
    rc = RetryCircuitService()
    rc.register("api", RetryCircuitConfig(max_retries=1, failure_threshold=2,
                                           recovery_timeout_s=0.001,
                                           success_threshold=2))
    def fail(): raise RuntimeError("err")
    rc.call("api", fail)
    rc.call("api", fail)
    import time; time.sleep(0.002)
    # Now half-open — success should start closing
    rc.call("api", lambda: "ok")
    rc.call("api", lambda: "ok")
    assert rc.get_state("api")["state"] == "closed"


def test_half_open_failure_reopens():
    rc = RetryCircuitService()
    rc.register("api", RetryCircuitConfig(max_retries=1, failure_threshold=2,
                                           recovery_timeout_s=0.001))
    def fail(): raise RuntimeError("err")
    rc.call("api", fail); rc.call("api", fail)
    import time; time.sleep(0.002)
    rc.call("api", fail)  # probe fails → back to open
    assert rc.get_state("api")["state"] == "open"


def test_success_resets_failures():
    rc = RetryCircuitService()
    rc.register("api", RetryCircuitConfig(max_retries=1, failure_threshold=3))
    def fail(): raise RuntimeError("err")
    rc.call("api", fail)
    rc.call("api", fail)
    rc.call("api", lambda: "ok")  # resets failure count
    rc.call("api", fail)  # only 1 failure now
    assert rc.get_state("api")["state"] == "closed"


def test_reset():
    rc = RetryCircuitService()
    rc.register("api", RetryCircuitConfig(max_retries=1, failure_threshold=1))
    rc.call("api", lambda: (_ for _ in ()).throw(RuntimeError("x")))
    assert rc.get_state("api")["state"] == "open"
    rc.reset("api")
    assert rc.get_state("api")["state"] == "closed"


def test_stats():
    rc = RetryCircuitService()
    rc.register("api")
    rc.call("api", lambda: 1)
    rc.call("api", lambda: 2)
    stats = rc.get_state("api")
    assert stats["total_calls"] == 2
    assert stats["success_rate"] == 100.0
