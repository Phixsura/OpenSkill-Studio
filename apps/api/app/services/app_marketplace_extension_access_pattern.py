"""Access Pattern Analyzer — detect anomalous API access patterns.

Detects:
- Time-of-day anomalies (requests at unusual hours)
- Velocity anomalies (sudden burst vs normal rate)
- Endpoint diversity anomalies (hitting many new endpoints)
- Geographic anomalies (requests from unexpected regions)
- Composite anomaly score with severity classification
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import math
import statistics
from collections import Counter, deque


@dataclass
class AccessEvent:
    timestamp: float
    endpoint: str
    ip_region: str = ""
    user_agent: str = ""
    status_code: int = 200


@dataclass
class AnomalyReport:
    score: float  # 0-100
    severity: str  # normal, suspicious, critical
    anomalies: list[str]
    recommendations: list[str]


class AccessPatternAnalyzerService:
    WINDOW_SIZE = 3600  # 1 hour analysis window
    HISTORY_HOURS = 24  # hours of baseline

    def __init__(self):
        self._events: dict[str, deque[AccessEvent]] = {}  # client_id -> events
        self._baselines: dict[str, dict] = {}  # client_id -> baseline stats

    def record(self, client_id: str, endpoint: str, ip_region: str = "",
               user_agent: str = "", status_code: int = 200) -> None:
        if client_id not in self._events:
            self._events[client_id] = deque(maxlen=50000)
        self._events[client_id].append(AccessEvent(
            timestamp=time.time(), endpoint=endpoint,
            ip_region=ip_region, user_agent=user_agent,
            status_code=status_code))

    def build_baseline(self, client_id: str) -> dict:
        """Build a usage fingerprint from historical data."""
        events = list(self._events.get(client_id, []))
        if len(events) < 10:
            return {"insufficient_data": True}

        # Hourly distribution
        hours = Counter()
        for e in events:
            h = int(e.timestamp % 86400 / 3600)
            hours[h] += 1

        # Endpoint distribution
        endpoints = Counter(e.endpoint for e in events)
        unique_endpoints = len(endpoints)

        # Request rate (per minute)
        if len(events) >= 2:
            duration = events[-1].timestamp - events[0].timestamp
            rpm = len(events) / max(1, duration / 60)
        else:
            rpm = 0

        # Regions
        regions = Counter(e.ip_region for e in events if e.ip_region)

        # Error rate
        errors = sum(1 for e in events if e.status_code >= 400)
        error_rate = errors / len(events) if events else 0

        baseline = {
            "event_count": len(events),
            "avg_rpm": round(rpm, 2),
            "peak_rpm": round(rpm * 2, 2),  # estimated peak
            "unique_endpoints": unique_endpoints,
            "top_endpoints": dict(endpoints.most_common(10)),
            "active_hours": set(hours.keys()),
            "known_regions": set(regions.keys()),
            "normal_error_rate": round(error_rate, 4),
        }
        self._baselines[client_id] = baseline
        return baseline

    def analyze(self, client_id: str, window_seconds: int = 300) -> AnomalyReport:
        """Analyze recent events against baseline."""
        baseline = self._baselines.get(client_id, {})
        events = list(self._events.get(client_id, []))

        now = time.time()
        recent = [e for e in events if e.timestamp > now - window_seconds]

        if not recent:
            return AnomalyReport(score=0, severity="normal", anomalies=[], recommendations=[])

        if baseline.get("insufficient_data"):
            return AnomalyReport(score=10, severity="normal",
                                 anomalies=["Insufficient baseline data"],
                                 recommendations=["Collect more data before analysis"])

        anomalies = []
        scores = []

        # 1. Velocity check
        duration = max(1, recent[-1].timestamp - recent[0].timestamp)
        current_rpm = len(recent) / (duration / 60)
        peak = baseline.get("peak_rpm", 100)
        if peak > 0 and current_rpm > peak * 3:
            ratio = current_rpm / peak
            anomalies.append(f"Velocity anomaly: {current_rpm:.0f} rpm vs peak {peak:.0f} ({ratio:.1f}x)")
            scores.append(min(40, ratio * 10))

        # 2. Time-of-day check
        current_hour = int(now % 86400 / 3600)
        active_hours = baseline.get("active_hours", set())
        if active_hours and current_hour not in active_hours:
            anomalies.append(f"Off-hours access: hour {current_hour} not in normal pattern")
            scores.append(20)

        # 3. Endpoint diversity
        recent_endpoints = set(e.endpoint for e in recent)
        known_endpoints = set(baseline.get("top_endpoints", {}).keys())
        new_endpoints = recent_endpoints - known_endpoints
        if known_endpoints and len(new_endpoints) > len(known_endpoints):
            anomalies.append(f"Endpoint scan: {len(new_endpoints)} unknown endpoints accessed")
            scores.append(30)

        # 4. Region check
        recent_regions = set(e.ip_region for e in recent if e.ip_region)
        known_regions = baseline.get("known_regions", set())
        new_regions = recent_regions - known_regions
        if known_regions and new_regions:
            anomalies.append(f"New regions: {new_regions}")
            scores.append(25)

        # 5. Error rate spike
        recent_errors = sum(1 for e in recent if e.status_code >= 400)
        recent_error_rate = recent_errors / len(recent) if recent else 0
        normal_error_rate = baseline.get("normal_error_rate", 0.05)
        if recent_error_rate > max(normal_error_rate * 3, 0.2):
            anomalies.append(f"Error spike: {recent_error_rate:.1%} vs normal {normal_error_rate:.1%}")
            scores.append(25)

        total_score = min(100, sum(scores))
        severity = "critical" if total_score >= 70 else "suspicious" if total_score >= 30 else "normal"

        recommendations = []
        if total_score >= 70:
            recommendations.append("Consider blocking this client immediately")
        elif total_score >= 30:
            recommendations.append("Enable enhanced logging and rate limiting")
        if new_regions:
            recommendations.append("Verify client identity — accessing from new location")

        return AnomalyReport(score=round(total_score, 1), severity=severity,
                             anomalies=anomalies, recommendations=recommendations)
