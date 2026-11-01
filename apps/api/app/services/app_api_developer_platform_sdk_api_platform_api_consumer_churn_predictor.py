"""App API Developer Consumer Churn Predictor — predict consumers at risk of churning."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ChurnPrediction:
    consumer_id: str
    days_since_last_call: int
    api_calls_trend_pct: float  # negative = declining
    error_rate_pct: float
    support_tickets_open: int

    @property
    def churn_risk_score(self) -> int:
        s = 0
        if self.days_since_last_call > 30: s += 30
        elif self.days_since_last_call > 14: s += 15
        if self.api_calls_trend_pct < -50: s += 30
        elif self.api_calls_trend_pct < -20: s += 15
        if self.error_rate_pct > 10: s += 20
        elif self.error_rate_pct > 5: s += 10
        if self.support_tickets_open >= 3: s += 20
        elif self.support_tickets_open >= 1: s += 10
        return min(100, s)

    @property
    def risk_level(self) -> str:
        s = self.churn_risk_score
        if s >= 70: return "critical"
        if s >= 40: return "high"
        if s >= 20: return "medium"
        return "low"

class AppAPIDeveloperPlatformSDKApiPlatformApiConsumerChurnPredictor:
    def __init__(self) -> None:
        self._predictions: dict[tuple[str, str], ChurnPrediction] = {}

    def predict(self, installation_id: str, consumer_id: str, **kwargs) -> ChurnPrediction:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        p = ChurnPrediction(consumer_id=consumer_id, days_since_last_call=kwargs.get("days_since_last_call", 0), api_calls_trend_pct=kwargs.get("api_calls_trend_pct", 0), error_rate_pct=kwargs.get("error_rate_pct", 0), support_tickets_open=kwargs.get("support_tickets_open", 0))
        self._predictions[key] = p
        return p

    def at_risk(self, installation_id: str, min_risk: str = "high") -> list[ChurnPrediction]:
        thresholds = {"low": 0, "medium": 20, "high": 40, "critical": 70}
        threshold = thresholds.get(min_risk, 40)
        return [p for (inst, _), p in self._predictions.items() if inst == installation_id and p.churn_risk_score >= threshold]

    def all_predictions(self, installation_id: str) -> list[ChurnPrediction]:
        return sorted([p for (inst, _), p in self._predictions.items() if inst == installation_id], key=lambda p: p.churn_risk_score, reverse=True)
