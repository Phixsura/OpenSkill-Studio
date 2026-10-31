"""Consumer API Request Transformer — modify incoming requests before processing."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import structlog

log = structlog.get_logger()

@dataclass
class RequestTransformRule:
    rule_id: str
    target: str  # "header", "query", "body"
    action: str  # "add", "remove", "rename", "set"
    field_name: str
    value: str = ""
    new_name: str = ""

@dataclass
class TransformResult:
    headers: dict[str, str]
    query_params: dict[str, str]
    body: dict
    rules_applied: int

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestTransformer:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], list[RequestTransformRule]] = {}

    def add_rule(self, installation_id: str, consumer_id: str, rule: RequestTransformRule) -> RequestTransformRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if rule.target not in ("header", "query", "body"):
            raise ValueError(f"Invalid target: {rule.target}")
        if rule.action not in ("add", "remove", "rename", "set"):
            raise ValueError(f"Invalid action: {rule.action}")
        key = (installation_id, consumer_id)
        if key not in self._rules:
            self._rules[key] = []
        self._rules[key].append(rule)
        return rule

    def transform(self, installation_id: str, consumer_id: str, headers: dict[str, str], query_params: dict[str, str], body: dict) -> TransformResult:
        rules = self._rules.get((installation_id, consumer_id), [])
        h = dict(headers)
        q = dict(query_params)
        b = dict(body)
        applied = 0
        for rule in rules:
            target = {"header": h, "query": q, "body": b}[rule.target]
            if rule.action == "add" and rule.field_name not in target:
                target[rule.field_name] = rule.value
                applied += 1
            elif rule.action == "set":
                target[rule.field_name] = rule.value
                applied += 1
            elif rule.action == "remove" and rule.field_name in target:
                del target[rule.field_name]
                applied += 1
            elif rule.action == "rename" and rule.field_name in target:
                target[rule.new_name] = target.pop(rule.field_name)
                applied += 1
        return TransformResult(headers=h, query_params=q, body=b, rules_applied=applied)

    def list_rules(self, installation_id: str, consumer_id: str) -> list[RequestTransformRule]:
        return self._rules.get((installation_id, consumer_id), [])

    def clear_rules(self, installation_id: str, consumer_id: str) -> int:
        key = (installation_id, consumer_id)
        count = len(self._rules.get(key, []))
        self._rules[key] = []
        return count
