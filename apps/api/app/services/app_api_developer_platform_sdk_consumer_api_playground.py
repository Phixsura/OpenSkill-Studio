"""Consumer API Playground — interactive API testing with saved collections."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()


@dataclass
class PlaygroundRequest:
    request_id: str
    name: str
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class PlaygroundResponse:
    status_code: int
    body: str
    headers: dict[str, str] = field(default_factory=dict)
    latency_ms: float = 0.0


@dataclass
class RequestHistory:
    request: PlaygroundRequest
    response: PlaygroundResponse | None = None
    executed_at: str = ""


@dataclass
class Collection:
    collection_id: str
    name: str
    requests: list[PlaygroundRequest] = field(default_factory=list)


@dataclass
class ApiPlayground:
    """Interactive API playground with collections and history."""

    _collections: dict[str, Collection] = field(default_factory=dict)
    _history: list[RequestHistory] = field(default_factory=list)
    _max_history: int = 500

    def create_collection(self, collection_id: str, name: str) -> dict:
        if collection_id in self._collections:
            raise ValueError(f"Collection {collection_id} already exists")
        self._collections[collection_id] = Collection(collection_id=collection_id, name=name)
        logger.info("collection_created", collection_id=collection_id)
        return {"collection_id": collection_id, "name": name}

    def add_request(self, collection_id: str, request: PlaygroundRequest) -> dict:
        coll = self._collections.get(collection_id)
        if not coll:
            raise ValueError(f"Collection {collection_id} not found")
        coll.requests.append(request)
        return {"collection_id": collection_id, "request_id": request.request_id,
                "total_requests": len(coll.requests)}

    def execute(self, request: PlaygroundRequest, status_code: int = 200,
                response_body: str = "", latency_ms: float = 0.0) -> dict:
        response = PlaygroundResponse(
            status_code=status_code, body=response_body,
            latency_ms=latency_ms,
        )
        entry = RequestHistory(
            request=request, response=response,
            executed_at=datetime.now(timezone.utc).isoformat(),
        )
        if len(self._history) >= self._max_history:
            self._history = self._history[-(self._max_history // 2):]
        self._history.append(entry)
        logger.info("request_executed", method=request.method, url=request.url)
        return {
            "request_id": request.request_id,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "body_length": len(response_body),
        }

    def get_history(self, limit: int = 20, method: str | None = None) -> list[dict]:
        items = list(reversed(self._history))
        if method:
            items = [h for h in items if h.request.method == method.upper()]
        return [
            {"request_id": h.request.request_id, "name": h.request.name,
             "method": h.request.method, "url": h.request.url,
             "status_code": h.response.status_code if h.response else None,
             "latency_ms": h.response.latency_ms if h.response else 0,
             "executed_at": h.executed_at}
            for h in items[:limit]
        ]

    def get_collection(self, collection_id: str) -> dict | None:
        coll = self._collections.get(collection_id)
        if not coll:
            return None
        return {
            "collection_id": coll.collection_id, "name": coll.name,
            "request_count": len(coll.requests),
            "requests": [{"id": r.request_id, "name": r.name,
                          "method": r.method, "url": r.url}
                         for r in coll.requests],
        }

    def list_collections(self) -> list[dict]:
        return [{"collection_id": c.collection_id, "name": c.name,
                 "request_count": len(c.requests)}
                for c in self._collections.values()]

    def delete_collection(self, collection_id: str) -> dict:
        if collection_id in self._collections:
            del self._collections[collection_id]
            return {"deleted": True}
        return {"deleted": False}

    def get_stats(self) -> dict:
        return {
            "collections": len(self._collections),
            "saved_requests": sum(len(c.requests) for c in self._collections.values()),
            "history_entries": len(self._history),
        }
