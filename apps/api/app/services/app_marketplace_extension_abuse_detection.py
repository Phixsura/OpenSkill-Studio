"""Abuse Detection — detect and prevent platform abuse by extensions.

Monitors for suspicious patterns: excessive API calls, scraping,
credential stuffing, and unauthorized data access attempts.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class AbuseSignal:
    signal_type: str   # rate_spike, scraping, credential_stuffing, data_exfil
    extension_id: str
    severity: str      # low, medium, high, critical
    evidence: dict
    detected_at: str = ""

    def __post_init__(self):
        if not self.detected_at:
            self.detected_at = datetime.now(timezone.utc).isoformat()


class AbuseDetectionService:
    """Detects platform abuse patterns from extensions."""

    def __init__(self, rate_threshold: int = 1000, error_threshold: float = 50.0):
        self._signals: list[AbuseSignal] = []
        self._request_counts: dict[str, int] = defaultdict(int)
        self._error_counts: dict[str, int] = defaultdict(int)
        self._unique_ips: dict[str, set[str]] = defaultdict(set)
        self._rate_threshold = rate_threshold
        self._error_threshold = error_threshold
        self._blocked: set[str] = set()

    def record_request(self, extension_id: str, ip: str = "",
                       status_code: int = 200, path: str = "") -> list[AbuseSignal]:
        """Record a request and check for abuse patterns."""
        self._request_counts[extension_id] += 1
        if status_code >= 400:
            self._error_counts[extension_id] += 1
        if ip:
            self._unique_ips[extension_id].add(ip)

        return self._analyze(extension_id)

    def _analyze(self, extension_id: str) -> list[AbuseSignal]:
        signals = []
        count = self._request_counts[extension_id]
        errors = self._error_counts[extension_id]
        ips = len(self._unique_ips[extension_id])

        # Rate spike detection
        if count > self._rate_threshold:
            signals.append(AbuseSignal(
                "rate_spike", extension_id, "high",
                {"requests": count, "threshold": self._rate_threshold},
            ))

        # High error rate (possible credential stuffing)
        if count > 100:
            error_rate = errors / count * 100
            if error_rate > self._error_threshold:
                signals.append(AbuseSignal(
                    "credential_stuffing", extension_id, "critical",
                    {"error_rate": round(error_rate, 1), "errors": errors, "total": count},
                ))

        # Too many unique IPs (possible distributed attack)
        if ips > 100:
            signals.append(AbuseSignal(
                "distributed_abuse", extension_id, "medium",
                {"unique_ips": ips},
            ))

        for s in signals:
            self._signals.append(s)
        return signals

    def block(self, extension_id: str) -> None:
        self._blocked.add(extension_id)

    def unblock(self, extension_id: str) -> None:
        self._blocked.discard(extension_id)

    def is_blocked(self, extension_id: str) -> bool:
        return extension_id in self._blocked

    def get_signals(self, extension_id: str | None = None,
                    severity: str | None = None) -> list[AbuseSignal]:
        signals = self._signals
        if extension_id:
            signals = [s for s in signals if s.extension_id == extension_id]
        if severity:
            signals = [s for s in signals if s.severity == severity]
        return signals

    def get_risk_score(self, extension_id: str) -> dict:
        signals = self.get_signals(extension_id)
        severity_weights = {"low": 1, "medium": 5, "high": 10, "critical": 25}
        score = sum(severity_weights.get(s.severity, 0) for s in signals)
        risk = "critical" if score >= 50 else "high" if score >= 20 else "medium" if score >= 5 else "low"
        return {"extension_id": extension_id, "score": score, "risk": risk,
                "signals": len(signals), "blocked": self.is_blocked(extension_id)}
