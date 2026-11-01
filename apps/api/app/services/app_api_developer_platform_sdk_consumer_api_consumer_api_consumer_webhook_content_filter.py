"""Consumer API Webhook Content Filter — filter webhook payloads by content rules."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class ContentFilterRule:
    rule_id: str
    field_path: str
    operator: str  # "equals", "contains", "not_equals", "regex", "exists", "not_exists"
    value: str = ""

@dataclass
class ContentFilter:
    filter_id: str
    webhook_id: str
    rules: list[ContentFilterRule] = field(default_factory=list)
    match_mode: str = "all"  # "all" (AND) or "any" (OR)

@dataclass
class FilterResult:
    passed: bool
    matched_rules: int
    total_rules: int
    reason: str

class AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerWebhookContentFilter:
    def __init__(self) -> None:
        self._filters: dict[tuple[str, str, str], ContentFilter] = {}

    def set_filter(self, installation_id: str, consumer_id: str, content_filter: ContentFilter) -> ContentFilter:
        if not installation_id:
            raise ValueError("installation_id is required")
        for rule in content_filter.rules:
            if rule.operator not in ("equals", "contains", "not_equals", "regex", "exists", "not_exists"):
                raise ValueError(f"Invalid operator: {rule.operator}")
        self._filters[(installation_id, consumer_id, content_filter.webhook_id)] = content_filter
        return content_filter

    def evaluate(self, installation_id: str, consumer_id: str, webhook_id: str, payload: dict) -> FilterResult:
        key = (installation_id, consumer_id, webhook_id)
        f = self._filters.get(key)
        if not f or not f.rules:
            return FilterResult(passed=True, matched_rules=0, total_rules=0, reason="no_filter")
        matched = 0
        for rule in f.rules:
            val = payload.get(rule.field_path)
            if rule.operator == "exists":
                if val is not None:
                    matched += 1
            elif rule.operator == "not_exists":
                if val is None:
                    matched += 1
            elif rule.operator == "equals":
                if str(val) == rule.value:
                    matched += 1
            elif rule.operator == "not_equals":
                if str(val) != rule.value:
                    matched += 1
            elif rule.operator == "contains":
                if isinstance(val, str) and rule.value in val:
                    matched += 1
            elif rule.operator == "regex":
                if isinstance(val, str) and re.search(rule.value, val):
                    matched += 1
        total = len(f.rules)
        if f.match_mode == "all":
            passed = matched == total
        else:
            passed = matched > 0
        reason = "all_matched" if passed and f.match_mode == "all" else ("any_matched" if passed else "no_match")
        return FilterResult(passed=passed, matched_rules=matched, total_rules=total, reason=reason)

    def get_filter(self, installation_id: str, consumer_id: str, webhook_id: str) -> ContentFilter | None:
        return self._filters.get((installation_id, consumer_id, webhook_id))
