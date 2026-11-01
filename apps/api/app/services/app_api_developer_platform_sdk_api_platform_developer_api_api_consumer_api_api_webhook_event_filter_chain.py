"""API Consumer Webhook Event Filter Chain — chain multiple filters for event delivery."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class FilterStep:
    step_id: str
    filter_type: str  # "event_type", "field_match", "payload_size", "consumer"
    config: dict[str, str] = field(default_factory=dict)
    inverted: bool = False  # if True, exclude matching events

VALID_FILTER_TYPES = {"event_type", "field_match", "payload_size", "consumer"}

@dataclass
class FilterChain:
    chain_id: str
    steps: list[FilterStep] = field(default_factory=list)
    mode: str = "all"  # "all" (AND) or "any" (OR)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventFilterChain:
    def __init__(self) -> None:
        self._chains: dict[tuple[str, str], FilterChain] = {}

    def create_chain(self, installation_id: str, chain: FilterChain) -> FilterChain:
        if not installation_id: raise ValueError("installation_id is required")
        if not chain.steps: raise ValueError("Chain must have at least one step")
        for s in chain.steps:
            if s.filter_type not in VALID_FILTER_TYPES: raise ValueError(f"Invalid filter: {s.filter_type}")
        if chain.mode not in ("all", "any"): raise ValueError("mode must be 'all' or 'any'")
        self._chains[(installation_id, chain.chain_id)] = chain
        return chain

    def evaluate(self, installation_id: str, chain_id: str, event_type: str, payload: dict, payload_size: int = 0, consumer_id: str = "") -> bool:
        chain = self._chains.get((installation_id, chain_id))
        if chain is None: return True
        results: list[bool] = []
        for s in chain.steps:
            match = self._eval_step(s, event_type, payload, payload_size, consumer_id)
            results.append(not match if s.inverted else match)
        if chain.mode == "all": return all(results)
        return any(results)

    def _eval_step(self, step: FilterStep, event_type: str, payload: dict, payload_size: int, consumer_id: str) -> bool:
        if step.filter_type == "event_type":
            pattern = step.config.get("pattern", "")
            if pattern.endswith(".*"): return event_type.startswith(pattern[:-2])
            return event_type == pattern
        elif step.filter_type == "field_match":
            field = step.config.get("field", "")
            value = step.config.get("value", "")
            return str(payload.get(field, "")) == value
        elif step.filter_type == "payload_size":
            max_bytes = int(step.config.get("max_bytes", "0"))
            return payload_size <= max_bytes if max_bytes > 0 else True
        elif step.filter_type == "consumer":
            return consumer_id == step.config.get("consumer_id", "")
        return True

    def list_chains(self, installation_id: str) -> list[FilterChain]:
        return [c for (inst, _), c in self._chains.items() if inst == installation_id]
