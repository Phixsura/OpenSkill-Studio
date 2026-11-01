"""Endpoint Request Sampler — probabilistic request sampling for analytics."""
from __future__ import annotations

import hashlib
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class SamplingRule:
    rule_id: str
    endpoint_id: str
    sample_rate: float  # 0.0 to 1.0
    conditions: dict = field(default_factory=dict)  # e.g. {"status_min": 400}


@dataclass
class SampledRequest:
    request_id: str
    endpoint_id: str
    method: str
    status_code: int
    latency_ms: float
    consumer_id: str = ""


@dataclass
class RequestSampler:
    """Probabilistic request sampling for analytics and debugging."""

    _rules: dict[str, SamplingRule] = field(default_factory=dict)  # endpoint -> rule
    _samples: list[SampledRequest] = field(default_factory=list)
    _total_evaluated: int = 0
    _max_samples: int = 10000

    def set_rule(self, rule: SamplingRule) -> dict:
        if not 0 <= rule.sample_rate <= 1:
            raise ValueError("sample_rate must be between 0 and 1")
        self._rules[rule.endpoint_id] = rule
        logger.info("sampling_rule_set", endpoint=rule.endpoint_id, rate=rule.sample_rate)
        return {"endpoint_id": rule.endpoint_id, "sample_rate": rule.sample_rate}

    def should_sample(self, request_id: str, endpoint_id: str) -> bool:
        rule = self._rules.get(endpoint_id)
        if not rule:
            return False
        if rule.sample_rate >= 1.0:
            return True
        if rule.sample_rate <= 0.0:
            return False
        # Deterministic hash-based sampling
        h = hashlib.md5(request_id.encode()).hexdigest()
        bucket = int(h[:8], 16) / 0xFFFFFFFF
        return bucket < rule.sample_rate

    def evaluate(self, request: SampledRequest) -> dict:
        self._total_evaluated += 1
        rule = self._rules.get(request.endpoint_id)
        if not rule:
            return {"sampled": False, "reason": "no_rule"}
        # Check conditions
        conditions = rule.conditions
        if "status_min" in conditions and request.status_code < conditions["status_min"]:
            return {"sampled": False, "reason": "condition_not_met"}
        if "latency_min_ms" in conditions and request.latency_ms < conditions["latency_min_ms"]:
            return {"sampled": False, "reason": "condition_not_met"}
        if not self.should_sample(request.request_id, request.endpoint_id):
            return {"sampled": False, "reason": "not_selected"}
        if len(self._samples) >= self._max_samples:
            self._samples = self._samples[-(self._max_samples // 2):]
        self._samples.append(request)
        return {"sampled": True, "total_samples": len(self._samples)}

    def get_samples(self, endpoint_id: str | None = None, limit: int = 50) -> list[dict]:
        samples = list(reversed(self._samples))
        if endpoint_id:
            samples = [s for s in samples if s.endpoint_id == endpoint_id]
        return [
            {"request_id": s.request_id, "endpoint_id": s.endpoint_id,
             "method": s.method, "status_code": s.status_code,
             "latency_ms": s.latency_ms}
            for s in samples[:limit]
        ]

    def get_stats(self) -> dict:
        return {
            "total_evaluated": self._total_evaluated,
            "total_sampled": len(self._samples),
            "sample_ratio": round(len(self._samples) / self._total_evaluated * 100, 2)
            if self._total_evaluated > 0 else 0,
            "rules_configured": len(self._rules),
        }

    def list_rules(self) -> list[dict]:
        return [
            {"endpoint_id": r.endpoint_id, "sample_rate": r.sample_rate,
             "conditions": r.conditions}
            for r in self._rules.values()
        ]

    def remove_rule(self, endpoint_id: str) -> dict:
        if endpoint_id in self._rules:
            del self._rules[endpoint_id]
            return {"removed": True}
        return {"removed": False}
