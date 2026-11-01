"""Capacity Planner — queuing theory based capacity estimation.

Uses Little's Law and M/M/1 queuing model to predict system behavior
under load and recommend capacity.

Implements:
- Little's Law: L = λW (items in system = arrival rate × wait time)
- M/M/1 utilization: ρ = λ/μ (arrival rate / service rate)
- Wait time prediction at given utilization
- Capacity recommendations for SLA targets
- What-if analysis for load changes
"""
from __future__ import annotations
from dataclasses import dataclass
import math


@dataclass
class SystemProfile:
    name: str
    arrival_rate: float  # requests per second (λ)
    service_rate: float  # requests per second per instance (μ)
    instances: int = 1
    sla_latency_ms: float = 200  # target p99 latency


@dataclass
class CapacityReport:
    utilization: float  # ρ (0-1)
    avg_queue_length: float  # L
    avg_wait_ms: float  # W
    avg_response_ms: float  # W_total (wait + service)
    throughput: float  # actual throughput
    meets_sla: bool
    headroom_pct: float  # how much more load before SLA breach


class CapacityPlannerService:
    def analyze(self, profile: SystemProfile) -> CapacityReport:
        """Analyze current capacity using M/M/c queuing model (simplified)."""
        total_service_rate = profile.service_rate * profile.instances
        utilization = profile.arrival_rate / total_service_rate if total_service_rate > 0 else 1.0

        if utilization >= 1.0:
            return CapacityReport(
                utilization=min(utilization, 1.0),
                avg_queue_length=float('inf'),
                avg_wait_ms=float('inf'),
                avg_response_ms=float('inf'),
                throughput=total_service_rate,
                meets_sla=False,
                headroom_pct=0)

        # M/M/1 approximation per instance
        rho = utilization
        service_time_ms = 1000 / profile.service_rate if profile.service_rate > 0 else float('inf')

        # Average time in system: 1/(μ-λ/c) simplified
        avg_response_ms = service_time_ms / (1 - rho)
        avg_wait_ms = avg_response_ms - service_time_ms

        # Little's Law: L = λ * W
        avg_queue_length = profile.arrival_rate * (avg_wait_ms / 1000)

        meets_sla = avg_response_ms <= profile.sla_latency_ms

        # Headroom: how much can λ increase before SLA breach
        # Find max λ where response_ms <= SLA
        # response = service_time / (1 - λ/μc) <= SLA
        # 1 - λ/μc >= service_time/SLA
        # λ <= μc * (1 - service_time/SLA)
        if profile.sla_latency_ms > service_time_ms:
            max_lambda = total_service_rate * (1 - service_time_ms / profile.sla_latency_ms)
            headroom = max(0, (max_lambda - profile.arrival_rate) / profile.arrival_rate * 100) \
                if profile.arrival_rate > 0 else 100
        else:
            headroom = 0

        return CapacityReport(
            utilization=round(rho, 4),
            avg_queue_length=round(avg_queue_length, 2),
            avg_wait_ms=round(avg_wait_ms, 2),
            avg_response_ms=round(avg_response_ms, 2),
            throughput=round(min(profile.arrival_rate, total_service_rate), 2),
            meets_sla=meets_sla,
            headroom_pct=round(headroom, 1))

    def recommend_instances(self, profile: SystemProfile,
                            target_utilization: float = 0.7) -> dict:
        """Recommend number of instances for target utilization."""
        needed = math.ceil(
            profile.arrival_rate / (profile.service_rate * target_utilization))
        needed = max(1, needed)

        # Analyze with recommended instances
        recommended_profile = SystemProfile(
            name=profile.name,
            arrival_rate=profile.arrival_rate,
            service_rate=profile.service_rate,
            instances=needed,
            sla_latency_ms=profile.sla_latency_ms)
        report = self.analyze(recommended_profile)

        return {
            "current_instances": profile.instances,
            "recommended_instances": needed,
            "change": needed - profile.instances,
            "target_utilization": target_utilization,
            "predicted_utilization": report.utilization,
            "predicted_response_ms": report.avg_response_ms,
            "meets_sla": report.meets_sla,
        }

    def what_if(self, profile: SystemProfile,
                load_multiplier: float) -> CapacityReport:
        """What-if analysis: predict behavior at N× current load."""
        scaled = SystemProfile(
            name=profile.name,
            arrival_rate=profile.arrival_rate * load_multiplier,
            service_rate=profile.service_rate,
            instances=profile.instances,
            sla_latency_ms=profile.sla_latency_ms)
        return self.analyze(scaled)

    def littles_law(self, arrival_rate: float, avg_time_in_system: float) -> dict:
        """Apply Little's Law: L = λW."""
        items_in_system = arrival_rate * avg_time_in_system
        return {
            "arrival_rate": arrival_rate,
            "avg_time_seconds": avg_time_in_system,
            "avg_items_in_system": round(items_in_system, 2),
        }
