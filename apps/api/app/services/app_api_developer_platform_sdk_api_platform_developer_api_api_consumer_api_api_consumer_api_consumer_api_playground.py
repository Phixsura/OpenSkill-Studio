"""Consumer API Playground — interactive API request builder and executor."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import json
import structlog

log = structlog.get_logger()

@dataclass
class PlaygroundRequest:
    request_id: str
    consumer_id: str
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str | None = None
    created_at: datetime | None = None

@dataclass
class PlaygroundResponse:
    request_id: str
    status_code: int
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    duration_ms: float = 0.0

@dataclass
class SavedRequest:
    name: str
    request: PlaygroundRequest
    description: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiPlayground:
    def __init__(self) -> None:
        self._history: dict[tuple[str, str], list[tuple[PlaygroundRequest, PlaygroundResponse]]] = {}
        self._saved: dict[tuple[str, str, str], SavedRequest] = {}  # (inst, consumer, name)

    def execute(self, installation_id: str, request: PlaygroundRequest) -> PlaygroundResponse:
        if not installation_id:
            raise ValueError("installation_id is required")
        if request.method.upper() not in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
            raise ValueError(f"Invalid method: {request.method}")
        if not request.path.startswith("/"):
            raise ValueError("Path must start with /")
        request.created_at = request.created_at or datetime.utcnow()
        # Simulated response for playground
        response = PlaygroundResponse(
            request_id=request.request_id,
            status_code=200,
            headers={"content-type": "application/json"},
            body=json.dumps({"data": {"message": "playground response", "method": request.method, "path": request.path}}),
            duration_ms=12.5,
        )
        key = (installation_id, request.consumer_id)
        if key not in self._history:
            self._history[key] = []
        self._history[key].append((request, response))
        if len(self._history[key]) > 100:
            self._history[key] = self._history[key][-100:]
        return response

    def save_request(self, installation_id: str, consumer_id: str, saved: SavedRequest) -> SavedRequest:
        if not saved.name:
            raise ValueError("name is required")
        self._saved[(installation_id, consumer_id, saved.name)] = saved
        return saved

    def list_saved(self, installation_id: str, consumer_id: str) -> list[SavedRequest]:
        return [s for (inst, cid, _), s in self._saved.items() if inst == installation_id and cid == consumer_id]

    def get_history(self, installation_id: str, consumer_id: str, limit: int = 20) -> list[tuple[PlaygroundRequest, PlaygroundResponse]]:
        return self._history.get((installation_id, consumer_id), [])[-limit:]
