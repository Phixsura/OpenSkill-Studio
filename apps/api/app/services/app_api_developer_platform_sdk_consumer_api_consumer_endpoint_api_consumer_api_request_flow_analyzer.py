"""Consumer API Request Flow Analyzer — analyze request flows and bottlenecks."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class FlowStep:
    step_id: str
    name: str
    service: str
    latency_ms: float
    status: str = "ok"  # "ok", "slow", "error"
    order: int = 0

@dataclass
class RequestFlow:
    flow_id: str
    consumer_id: str
    endpoint: str
    total_latency_ms: float
    steps: list[FlowStep] = field(default_factory=list)
    timestamp: datetime | None = None

@dataclass
class FlowAnalysis:
    total_flows: int
    avg_latency_ms: float
    bottleneck_service: str
    bottleneck_avg_ms: float
    slowest_step: str
    error_count: int

class AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiRequestFlowAnalyzer:
    def __init__(self) -> None:
        self._flows: dict[tuple[str, str], list[RequestFlow]] = {}

    def record_flow(self, installation_id: str, flow: RequestFlow) -> RequestFlow:
        if not installation_id:
            raise ValueError("installation_id is required")
        flow.timestamp = flow.timestamp or datetime.utcnow()
        flow.steps.sort(key=lambda s: s.order)
        key = (installation_id, flow.consumer_id)
        if key not in self._flows:
            self._flows[key] = []
        self._flows[key].append(flow)
        if len(self._flows[key]) > 5000:
            self._flows[key] = self._flows[key][-5000:]
        return flow

    def analyze(self, installation_id: str, consumer_id: str) -> FlowAnalysis:
        flows = self._flows.get((installation_id, consumer_id), [])
        if not flows:
            return FlowAnalysis(total_flows=0, avg_latency_ms=0, bottleneck_service="", bottleneck_avg_ms=0, slowest_step="", error_count=0)
        avg_lat = sum(f.total_latency_ms for f in flows) / len(flows)
        # Find bottleneck service
        service_latencies: dict[str, list[float]] = {}
        step_latencies: dict[str, list[float]] = {}
        errors = 0
        for f in flows:
            for s in f.steps:
                service_latencies.setdefault(s.service, []).append(s.latency_ms)
                step_latencies.setdefault(s.name, []).append(s.latency_ms)
                if s.status == "error":
                    errors += 1
        bottleneck_svc = ""
        bottleneck_avg = 0.0
        for svc, lats in service_latencies.items():
            avg = sum(lats) / len(lats)
            if avg > bottleneck_avg:
                bottleneck_avg = avg
                bottleneck_svc = svc
        slowest = ""
        slowest_avg = 0.0
        for step, lats in step_latencies.items():
            avg = sum(lats) / len(lats)
            if avg > slowest_avg:
                slowest_avg = avg
                slowest = step
        return FlowAnalysis(total_flows=len(flows), avg_latency_ms=round(avg_lat, 1), bottleneck_service=bottleneck_svc, bottleneck_avg_ms=round(bottleneck_avg, 1), slowest_step=slowest, error_count=errors)

    def get_recent(self, installation_id: str, consumer_id: str, limit: int = 10) -> list[RequestFlow]:
        return list(reversed(self._flows.get((installation_id, consumer_id), [])[-limit:]))
