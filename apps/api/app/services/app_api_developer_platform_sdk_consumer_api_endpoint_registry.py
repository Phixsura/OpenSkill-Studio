"""Consumer API Endpoint Registry — centralized endpoint metadata registry."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

ENDPOINT_STATUSES = ("active", "deprecated", "beta", "internal", "disabled")


@dataclass
class EndpointMeta:
    endpoint_id: str
    path: str
    method: str
    version: str
    status: str = "active"
    owner_team: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    rate_limit: int = 0
    auth_required: bool = True


@dataclass
class EndpointRegistry:
    """Centralized registry for all API endpoints with metadata."""

    _endpoints: dict[str, EndpointMeta] = field(default_factory=dict)

    def register(self, endpoint: EndpointMeta) -> dict:
        if endpoint.endpoint_id in self._endpoints:
            raise ValueError(f"Endpoint {endpoint.endpoint_id} already registered")
        if endpoint.status not in ENDPOINT_STATUSES:
            raise ValueError(f"Invalid status: {endpoint.status}")
        if not endpoint.path.startswith("/"):
            raise ValueError("Path must start with /")
        self._endpoints[endpoint.endpoint_id] = endpoint
        logger.info("endpoint_registered", endpoint_id=endpoint.endpoint_id)
        return {"endpoint_id": endpoint.endpoint_id, "path": endpoint.path}

    def update(self, endpoint_id: str, **kwargs) -> dict:
        ep = self._endpoints.get(endpoint_id)
        if not ep:
            raise ValueError(f"Endpoint {endpoint_id} not found")
        if "status" in kwargs and kwargs["status"] not in ENDPOINT_STATUSES:
            raise ValueError(f"Invalid status: {kwargs['status']}")
        for key, value in kwargs.items():
            if hasattr(ep, key):
                setattr(ep, key, value)
        return {"endpoint_id": endpoint_id, "updated": True}

    def get(self, endpoint_id: str) -> dict | None:
        ep = self._endpoints.get(endpoint_id)
        if not ep:
            return None
        return {
            "endpoint_id": ep.endpoint_id, "path": ep.path, "method": ep.method,
            "version": ep.version, "status": ep.status, "owner_team": ep.owner_team,
            "description": ep.description, "tags": ep.tags,
            "rate_limit": ep.rate_limit, "auth_required": ep.auth_required,
        }

    def search(self, query: str | None = None, tag: str | None = None,
               status: str | None = None, method: str | None = None) -> list[dict]:
        results = list(self._endpoints.values())
        if query:
            q = query.lower()
            results = [e for e in results if q in e.path.lower() or q in e.description.lower()]
        if tag:
            results = [e for e in results if tag in e.tags]
        if status:
            results = [e for e in results if e.status == status]
        if method:
            results = [e for e in results if e.method.upper() == method.upper()]
        return [self.get(e.endpoint_id) for e in results]

    def deregister(self, endpoint_id: str) -> dict:
        if endpoint_id in self._endpoints:
            del self._endpoints[endpoint_id]
            return {"removed": True}
        return {"removed": False}

    def get_by_team(self, team: str) -> list[dict]:
        return [self.get(e.endpoint_id) for e in self._endpoints.values() if e.owner_team == team]

    def get_stats(self) -> dict:
        eps = list(self._endpoints.values())
        by_status = {}
        for s in ENDPOINT_STATUSES:
            by_status[s] = sum(1 for e in eps if e.status == s)
        by_method: dict[str, int] = {}
        for e in eps:
            by_method[e.method] = by_method.get(e.method, 0) + 1
        return {
            "total": len(eps),
            "by_status": by_status,
            "by_method": by_method,
            "teams": len(set(e.owner_team for e in eps if e.owner_team)),
        }
