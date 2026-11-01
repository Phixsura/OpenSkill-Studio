"""Service Health Checker — endpoint health probes with circuit breaker."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class HealthProbe:
    endpoint_id: str
    timestamp: str
    healthy: bool
    latency_ms: float = 0.0
    status_code: int = 200
    error: str = ""


@dataclass
class CircuitState:
    state: str = "closed"  # closed, open, half_open
    failure_count: int = 0
    success_count: int = 0
    last_failure: str = ""
    failure_threshold: int = 5
    recovery_probes: int = 3


@dataclass
class HealthChecker:
    """Monitor endpoint health with circuit breaker pattern."""

    _probes: dict[str, list[HealthProbe]] = field(default_factory=dict)
    _circuits: dict[str, CircuitState] = field(default_factory=dict)

    def configure_circuit(self, endpoint_id: str, failure_threshold: int = 5,
                          recovery_probes: int = 3) -> dict:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be positive")
        self._circuits[endpoint_id] = CircuitState(
            failure_threshold=failure_threshold,
            recovery_probes=recovery_probes,
        )
        return {"endpoint_id": endpoint_id, "configured": True}

    def record_probe(self, probe: HealthProbe) -> dict:
        self._probes.setdefault(probe.endpoint_id, []).append(probe)
        circuit = self._circuits.setdefault(probe.endpoint_id, CircuitState())
        if probe.healthy:
            if circuit.state == "half_open":
                circuit.success_count += 1
                if circuit.success_count >= circuit.recovery_probes:
                    circuit.state = "closed"
                    circuit.failure_count = 0
                    circuit.success_count = 0
                    logger.info("circuit_closed", endpoint_id=probe.endpoint_id)
            elif circuit.state == "closed":
                circuit.failure_count = max(0, circuit.failure_count - 1)
        else:
            circuit.last_failure = probe.timestamp
            if circuit.state == "half_open":
                circuit.state = "open"
                circuit.success_count = 0
                logger.info("circuit_reopened", endpoint_id=probe.endpoint_id)
            elif circuit.state == "closed":
                circuit.failure_count += 1
                if circuit.failure_count >= circuit.failure_threshold:
                    circuit.state = "open"
                    logger.info("circuit_opened", endpoint_id=probe.endpoint_id)
        return {"endpoint_id": probe.endpoint_id, "circuit_state": circuit.state}

    def try_half_open(self, endpoint_id: str) -> dict:
        circuit = self._circuits.get(endpoint_id)
        if not circuit:
            return {"error": "no_circuit"}
        if circuit.state != "open":
            return {"error": "not_open", "state": circuit.state}
        circuit.state = "half_open"
        circuit.success_count = 0
        return {"endpoint_id": endpoint_id, "state": "half_open"}

    def get_status(self, endpoint_id: str) -> dict:
        probes = self._probes.get(endpoint_id, [])
        circuit = self._circuits.get(endpoint_id, CircuitState())
        if not probes:
            return {"endpoint_id": endpoint_id, "status": "unknown", "circuit": circuit.state}
        recent = probes[-10:]
        healthy_count = sum(1 for p in recent if p.healthy)
        avg_latency = sum(p.latency_ms for p in recent) / len(recent) if recent else 0
        uptime_pct = healthy_count / len(recent) * 100
        if uptime_pct >= 99:
            status = "healthy"
        elif uptime_pct >= 90:
            status = "degraded"
        else:
            status = "unhealthy"
        return {
            "endpoint_id": endpoint_id,
            "status": status,
            "circuit": circuit.state,
            "uptime_pct": round(uptime_pct, 1),
            "avg_latency_ms": round(avg_latency, 2),
            "total_probes": len(probes),
            "recent_healthy": healthy_count,
            "recent_total": len(recent),
        }

    def list_endpoints(self) -> list[dict]:
        results = []
        for eid in self._probes:
            results.append(self.get_status(eid))
        results.sort(key=lambda x: x.get("uptime_pct", 0))
        return results
