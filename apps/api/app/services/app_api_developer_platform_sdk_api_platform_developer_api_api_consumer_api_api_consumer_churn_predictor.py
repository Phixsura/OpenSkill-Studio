"""API Consumer Churn Predictor — predict consumer churn risk from usage patterns."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ChurnSignals:
    consumer_id: str
    requests_decline_pct: float = 0.0  # negative = growth
    days_since_last_request: int = 0
    error_rate_increase_pct: float = 0.0
    support_tickets_open: int = 0
    feature_adoption_pct: float = 100.0

@dataclass
class ChurnPrediction:
    consumer_id: str
    churn_risk_pct: float
    risk_level: str  # "low", "medium", "high", "critical"
    top_signal: str

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerChurnPredictor:
    def __init__(self) -> None:
        self._signals: dict[tuple[str, str], ChurnSignals] = {}

    def update_signals(self, installation_id: str, signals: ChurnSignals) -> ChurnSignals:
        if not installation_id: raise ValueError("installation_id is required")
        self._signals[(installation_id, signals.consumer_id)] = signals
        return signals

    def predict(self, installation_id: str, consumer_id: str) -> ChurnPrediction:
        s = self._signals.get((installation_id, consumer_id))
        if s is None: return ChurnPrediction(consumer_id=consumer_id, churn_risk_pct=0, risk_level="low", top_signal="none")
        risk = 0.0
        top = "none"
        # Decline in usage (30%)
        if s.requests_decline_pct > 0:
            risk += min(30, s.requests_decline_pct * 0.6)
            if s.requests_decline_pct > 30: top = "usage_decline"
        # Inactivity (25%)
        if s.days_since_last_request > 0:
            risk += min(25, s.days_since_last_request * 1.5)
            if s.days_since_last_request > 14 and top == "none": top = "inactivity"
        # Error rate increase (20%)
        risk += min(20, s.error_rate_increase_pct * 0.4)
        # Support tickets (15%)
        risk += min(15, s.support_tickets_open * 3)
        if s.support_tickets_open > 3 and top == "none": top = "support_issues"
        # Low feature adoption (10%)
        risk += max(0, (100 - s.feature_adoption_pct) * 0.1)
        risk = round(min(100, risk), 1)
        level = "critical" if risk >= 75 else "high" if risk >= 50 else "medium" if risk >= 25 else "low"
        return ChurnPrediction(consumer_id=consumer_id, churn_risk_pct=risk, risk_level=level, top_signal=top or "mixed")

    def at_risk(self, installation_id: str, threshold_pct: float = 50.0) -> list[ChurnPrediction]:
        return [self.predict(installation_id, cid) for (inst, cid) in self._signals if inst == installation_id and self.predict(installation_id, cid).churn_risk_pct >= threshold_pct]

    def list_predictions(self, installation_id: str) -> list[ChurnPrediction]:
        return [self.predict(installation_id, cid) for (inst, cid) in self._signals if inst == installation_id]
