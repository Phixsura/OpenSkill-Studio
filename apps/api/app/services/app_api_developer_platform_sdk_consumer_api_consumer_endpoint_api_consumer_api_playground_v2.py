"""Consumer API Playground V2 — enhanced request builder with history and collections."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import json
import structlog

log = structlog.get_logger()

@dataclass
class PlaygroundRequest:
    request_id: str
    name: str
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    description: str = ""

@dataclass
class PlaygroundCollection:
    collection_id: str
    name: str
    requests: list[PlaygroundRequest] = field(default_factory=list)
    created_at: datetime | None = None

@dataclass
class ExecutionResult:
    request_id: str
    status_code: int
    response_body: str
    latency_ms: float
    executed_at: datetime

class AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiPlaygroundV2:
    def __init__(self) -> None:
        self._collections: dict[tuple[str, str, str], PlaygroundCollection] = {}
        self._history: dict[tuple[str, str], list[ExecutionResult]] = {}

    def create_collection(self, installation_id: str, consumer_id: str, collection: PlaygroundCollection) -> PlaygroundCollection:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not collection.name:
            raise ValueError("name is required")
        collection.created_at = collection.created_at or datetime.utcnow()
        key = (installation_id, consumer_id, collection.collection_id)
        if key in self._collections:
            raise ValueError(f"Collection {collection.collection_id} already exists")
        self._collections[key] = collection
        return collection

    def add_request(self, installation_id: str, consumer_id: str, collection_id: str, request: PlaygroundRequest) -> PlaygroundRequest:
        key = (installation_id, consumer_id, collection_id)
        coll = self._collections.get(key)
        if not coll:
            raise ValueError("Collection not found")
        if request.method.upper() not in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
            raise ValueError(f"Invalid method: {request.method}")
        coll.requests.append(request)
        return request

    def execute(self, installation_id: str, consumer_id: str, request: PlaygroundRequest, now: datetime) -> ExecutionResult:
        # Simulated execution
        result = ExecutionResult(request_id=request.request_id, status_code=200, response_body=json.dumps({"message": "ok", "method": request.method, "path": request.path}), latency_ms=15.0, executed_at=now)
        hkey = (installation_id, consumer_id)
        if hkey not in self._history:
            self._history[hkey] = []
        self._history[hkey].append(result)
        if len(self._history[hkey]) > 500:
            self._history[hkey] = self._history[hkey][-500:]
        return result

    def get_history(self, installation_id: str, consumer_id: str, limit: int = 20) -> list[ExecutionResult]:
        return list(reversed(self._history.get((installation_id, consumer_id), [])[-limit:]))

    def list_collections(self, installation_id: str, consumer_id: str) -> list[PlaygroundCollection]:
        return [c for (inst, cid, _), c in self._collections.items() if inst == installation_id and cid == consumer_id]
