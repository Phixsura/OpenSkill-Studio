from app.services.app_marketplace_app_app_app_app_app_app_app_circuit_fsm import CircuitFSM

def test_full_cycle():
    fsm = CircuitFSM(failure_threshold=3, success_threshold=2)
    assert fsm.state == "closed"
    for _ in range(3):
        fsm.on_failure()
    assert fsm.state == "open"
    fsm.on_timeout()
    assert fsm.state == "half_open"
    fsm.on_success()
    fsm.on_success()
    assert fsm.state == "closed"
    assert len(fsm.history()) == 3

def test_half_open_failure():
    fsm = CircuitFSM(failure_threshold=2)
    fsm.on_failure()
    fsm.on_failure()
    fsm.on_timeout()
    assert fsm.state == "half_open"
    fsm.on_failure()
    assert fsm.state == "open"
