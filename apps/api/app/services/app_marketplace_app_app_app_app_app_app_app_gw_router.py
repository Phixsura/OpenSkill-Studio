"""API gateway request router — route requests by path, header, and weight."""
from __future__ import annotations
import hashlib


class GatewayRouter:
    def __init__(self):
        self._routes: list[dict] = []

    def add_route(self, path_prefix: str, backend: str, weight: int = 100,
                  header_match: dict | None = None) -> dict:
        self._routes.append({"path_prefix": path_prefix, "backend": backend,
                              "weight": weight, "header_match": header_match or {}})
        return {"added": True, "total_routes": len(self._routes)}

    def match(self, path: str, headers: dict | None = None) -> dict:
        headers = headers or {}
        candidates = []
        for r in self._routes:
            if not path.startswith(r["path_prefix"]):
                continue
            if r["header_match"]:
                if not all(headers.get(k) == v for k, v in r["header_match"].items()):
                    continue
            candidates.append(r)
        if not candidates:
            return {"matched": False, "backend": "default"}
        # Weight-based selection among candidates
        candidates.sort(key=lambda c: -c["weight"])
        return {"matched": True, "backend": candidates[0]["backend"],
                "path_prefix": candidates[0]["path_prefix"]}

    def list_routes(self) -> list[dict]:
        return list(self._routes)
