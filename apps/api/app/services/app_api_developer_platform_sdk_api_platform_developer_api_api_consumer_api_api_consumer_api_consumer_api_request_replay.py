"""Consumer API Request Replay — replay historical requests for debugging."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import json
import structlog

log = structlog.get_logger()

@dataclass
class ReplayableRequest:
    request_id: str
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str | None = None
    original_status: int = 200
    original_at: datetime | None = None

@dataclass
class ReplayResult:
    replay_id: str
    original_request_id: str
    replayed_at: datetime
    original_status: int
    replay_status: int
    diff_detected: bool
    diff_summary: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestReplay:
    def __init__(self, max_stored: int = 1000) -> None:
        self._requests: dict[tuple[str, str, str], ReplayableRequest] = {}  # (inst, consumer, req_id)
        self._replays: dict[tuple[str, str], list[ReplayResult]] = {}
        self._max = max_stored

    def store(self, installation_id: str, consumer_id: str, request: ReplayableRequest) -> ReplayableRequest:
        if not installation_id:
            raise ValueError("installation_id is required")
        # Redact auth headers before storing
        safe_headers = {k: ("***" if any(s in k.lower() for s in ("auth", "token", "key", "secret", "cookie")) else v) for k, v in request.headers.items()}
        request.headers = safe_headers
        key = (installation_id, consumer_id, request.request_id)
        self._requests[key] = request
        return request

    def replay(self, installation_id: str, consumer_id: str, request_id: str, now: datetime) -> ReplayResult:
        key = (installation_id, consumer_id, request_id)
        request = self._requests.get(key)
        if not request:
            raise ValueError("Request not found")
        # Simulated replay
        replay_status = request.original_status
        diff = False
        summary = "Identical response"
        result = ReplayResult(replay_id=f"rp-{now.isoformat()}", original_request_id=request_id, replayed_at=now, original_status=request.original_status, replay_status=replay_status, diff_detected=diff, diff_summary=summary)
        rkey = (installation_id, consumer_id)
        if rkey not in self._replays:
            self._replays[rkey] = []
        self._replays[rkey].append(result)
        return result

    def get_stored(self, installation_id: str, consumer_id: str, limit: int = 20) -> list[ReplayableRequest]:
        return [r for (inst, cid, _), r in self._requests.items() if inst == installation_id and cid == consumer_id][-limit:]

    def get_replays(self, installation_id: str, consumer_id: str, limit: int = 20) -> list[ReplayResult]:
        return self._replays.get((installation_id, consumer_id), [])[-limit:]
