"""CORS policy manager — manage cross-origin resource sharing policies."""
from __future__ import annotations


class CorsPolicyManager:
    def __init__(self):
        self._policies: dict[str, dict] = {}

    def set_policy(self, origin: str, methods: list[str] | None = None,
                   headers: list[str] | None = None, max_age: int = 3600,
                   credentials: bool = False) -> dict:
        self._policies[origin] = {
            "origin": origin,
            "methods": methods or ["GET", "POST", "PUT", "DELETE"],
            "headers": headers or ["Content-Type", "Authorization"],
            "max_age": max_age, "credentials": credentials}
        return self._policies[origin]

    def check(self, request_origin: str, method: str) -> dict:
        if "*" in self._policies:
            policy = self._policies["*"]
        elif request_origin in self._policies:
            policy = self._policies[request_origin]
        else:
            return {"allowed": False, "reason": "origin_not_allowed"}
        if method not in policy["methods"]:
            return {"allowed": False, "reason": "method_not_allowed"}
        return {"allowed": True, "origin": policy["origin"],
                "headers": policy["headers"], "max_age": policy["max_age"],
                "credentials": policy["credentials"]}

    def list_policies(self) -> list[dict]:
        return list(self._policies.values())
