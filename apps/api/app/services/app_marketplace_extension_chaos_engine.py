"""Chaos Engineering — controlled fault injection for resilience testing.

Netflix Chaos Monkey-style: inject failures to verify system resilience.

Implements:
- Fault types: latency, error, kill, resource exhaustion
- Blast radius control (percentage of requests affected)
- Duration-limited experiments
- Steady-state hypothesis verification
- Experiment scheduling and history
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import random
import hashlib


@dataclass
class Fault:
    fault_type: str  # latency, error, kill, memory, cpu
    target: str  # service or endpoint
    intensity: float  # 0-1 (e.g., 0.5 = 500ms latency, or 50% error rate)
    blast_radius: float = 0.1  # fraction of requests affected


@dataclass
class Experiment:
    experiment_id: str
    name: str
    hypothesis: str  # what we expect to hold true
    fault: Fault
    duration_seconds: float
    started_at: float = 0.0
    ended_at: float = 0.0
    status: str = "pending"  # pending, running, completed, aborted
    results: dict = field(default_factory=dict)


class ChaosEngineService:
    def __init__(self, seed: int | None = None):
        self._experiments: dict[str, Experiment] = {}
        self._active_faults: dict[str, Fault] = {}  # target -> fault
        self._counter = 0
        self._rng = random.Random(seed)
        self._metrics: dict[str, list[float]] = {}  # metric_name -> values

    def create_experiment(self, name: str, hypothesis: str, fault: Fault,
                          duration_seconds: float = 60) -> Experiment:
        self._counter += 1
        exp = Experiment(experiment_id=f"chaos-{self._counter}",
                         name=name, hypothesis=hypothesis,
                         fault=fault, duration_seconds=duration_seconds)
        self._experiments[exp.experiment_id] = exp
        return exp

    def start(self, experiment_id: str) -> bool:
        exp = self._experiments.get(experiment_id)
        if not exp or exp.status != "pending":
            return False
        exp.status = "running"
        exp.started_at = time.time()
        self._active_faults[exp.fault.target] = exp.fault
        return True

    def stop(self, experiment_id: str) -> Experiment | None:
        exp = self._experiments.get(experiment_id)
        if not exp or exp.status != "running":
            return None
        exp.status = "completed"
        exp.ended_at = time.time()
        self._active_faults.pop(exp.fault.target, None)
        return exp

    def abort(self, experiment_id: str) -> bool:
        exp = self._experiments.get(experiment_id)
        if not exp or exp.status != "running":
            return False
        exp.status = "aborted"
        exp.ended_at = time.time()
        self._active_faults.pop(exp.fault.target, None)
        return True

    def should_inject(self, target: str, request_id: str = "") -> dict | None:
        """Check if a fault should be injected for this request.
        Returns fault details or None if request is not affected."""
        fault = self._active_faults.get(target)
        if not fault:
            return None

        # Deterministic based on request_id for reproducibility
        if request_id:
            h = int(hashlib.md5(request_id.encode()).hexdigest()[:8], 16)
            affected = (h % 10000) < int(fault.blast_radius * 10000)
        else:
            affected = self._rng.random() < fault.blast_radius

        if not affected:
            return None

        result = {"fault_type": fault.fault_type, "target": fault.target}

        if fault.fault_type == "latency":
            result["delay_ms"] = int(fault.intensity * 1000)
        elif fault.fault_type == "error":
            result["status_code"] = 500
            result["message"] = "Chaos: injected error"
        elif fault.fault_type == "kill":
            result["action"] = "terminate"
        elif fault.fault_type == "memory":
            result["pressure_mb"] = int(fault.intensity * 1024)
        elif fault.fault_type == "cpu":
            result["load_pct"] = int(fault.intensity * 100)

        return result

    def record_metric(self, name: str, value: float) -> None:
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(value)

    def verify_hypothesis(self, experiment_id: str, metric_name: str,
                          threshold: float, comparator: str = "lt") -> dict:
        """Verify steady-state hypothesis against recorded metrics."""
        exp = self._experiments.get(experiment_id)
        if not exp:
            return {"verified": False, "reason": "experiment not found"}

        values = self._metrics.get(metric_name, [])
        if not values:
            return {"verified": False, "reason": "no metrics recorded"}

        avg = sum(values) / len(values)

        if comparator == "lt":
            passed = avg < threshold
        elif comparator == "gt":
            passed = avg > threshold
        elif comparator == "eq":
            passed = abs(avg - threshold) < 0.01
        else:
            passed = False

        exp.results = {"metric": metric_name, "avg_value": round(avg, 4),
                       "threshold": threshold, "passed": passed}
        return exp.results

    def get_active_experiments(self) -> list[Experiment]:
        return [e for e in self._experiments.values() if e.status == "running"]

    def tick(self) -> list[str]:
        """Auto-stop expired experiments."""
        stopped = []
        now = time.time()
        for exp in list(self._experiments.values()):
            if exp.status == "running":
                if now - exp.started_at >= exp.duration_seconds:
                    self.stop(exp.experiment_id)
                    stopped.append(exp.experiment_id)
        return stopped
