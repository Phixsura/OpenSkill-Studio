from app.services.app_marketplace_extension_chaos_engine import (
    ChaosEngineService, Fault
)


def test_create_and_start():
    chaos = ChaosEngineService(seed=42)
    exp = chaos.create_experiment(
        "Latency Test", "P99 stays under 500ms",
        Fault("latency", "api-gateway", intensity=0.3, blast_radius=0.1))
    assert chaos.start(exp.experiment_id) is True
    assert exp.status == "running"


def test_fault_injection():
    chaos = ChaosEngineService(seed=42)
    exp = chaos.create_experiment(
        "Error Injection", "Error rate stays under 5%",
        Fault("error", "user-service", intensity=1.0, blast_radius=1.0))
    chaos.start(exp.experiment_id)
    result = chaos.should_inject("user-service")
    assert result is not None
    assert result["fault_type"] == "error"
    assert result["status_code"] == 500


def test_blast_radius():
    chaos = ChaosEngineService(seed=42)
    exp = chaos.create_experiment(
        "Blast Test", "Hypothesis",
        Fault("latency", "svc", intensity=0.5, blast_radius=0.3))
    chaos.start(exp.experiment_id)
    affected = sum(1 for i in range(1000)
                   if chaos.should_inject("svc", f"req-{i}"))
    # ~30% should be affected
    assert 200 < affected < 400


def test_no_fault_when_stopped():
    chaos = ChaosEngineService(seed=42)
    exp = chaos.create_experiment(
        "Test", "H", Fault("error", "svc", 1.0, 1.0))
    chaos.start(exp.experiment_id)
    chaos.stop(exp.experiment_id)
    assert chaos.should_inject("svc") is None


def test_abort():
    chaos = ChaosEngineService()
    exp = chaos.create_experiment("T", "H", Fault("kill", "svc", 1.0, 0.5))
    chaos.start(exp.experiment_id)
    assert chaos.abort(exp.experiment_id) is True
    assert exp.status == "aborted"
    assert chaos.should_inject("svc") is None


def test_hypothesis_verification():
    chaos = ChaosEngineService()
    exp = chaos.create_experiment("T", "Error rate < 5%",
                                  Fault("error", "svc", 1.0, 0.1))
    chaos.start(exp.experiment_id)
    # Record some error rates
    for rate in [2.0, 3.5, 4.0, 3.0, 2.5]:
        chaos.record_metric("error_rate", rate)
    result = chaos.verify_hypothesis(exp.experiment_id, "error_rate", 5.0, "lt")
    assert result["passed"] is True
    assert result["avg_value"] == 3.0


def test_hypothesis_fails():
    chaos = ChaosEngineService()
    exp = chaos.create_experiment("T", "Latency < 100ms",
                                  Fault("latency", "svc", 0.5, 0.5))
    chaos.start(exp.experiment_id)
    for v in [150, 200, 180, 220]:
        chaos.record_metric("p99_latency", v)
    result = chaos.verify_hypothesis(exp.experiment_id, "p99_latency", 100.0, "lt")
    assert result["passed"] is False


def test_latency_fault_details():
    chaos = ChaosEngineService()
    exp = chaos.create_experiment("T", "H",
                                  Fault("latency", "svc", intensity=0.5, blast_radius=1.0))
    chaos.start(exp.experiment_id)
    result = chaos.should_inject("svc")
    assert result["delay_ms"] == 500


def test_auto_stop_expired():
    chaos = ChaosEngineService()
    exp = chaos.create_experiment("T", "H",
                                  Fault("error", "svc", 1.0, 1.0),
                                  duration_seconds=0.01)
    chaos.start(exp.experiment_id)
    import time; time.sleep(0.02)
    stopped = chaos.tick()
    assert exp.experiment_id in stopped
    assert exp.status == "completed"
