"""Playground History — save and replay API playground sessions.

Stores request/response pairs, collections, environment variables,
and enables sharing of API test scenarios.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class SavedRequest:
    request_id: str
    name: str
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    response_status: int = 0
    response_body: str = ""
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class Collection:
    collection_id: str
    name: str
    description: str = ""
    requests: list[str] = field(default_factory=list)  # request_ids


class PlaygroundHistoryService:
    """Manages saved API playground requests and collections."""

    def __init__(self):
        self._requests: dict[str, dict[str, SavedRequest]] = defaultdict(dict)
        self._collections: dict[str, dict[str, Collection]] = defaultdict(dict)

    def save_request(self, user_id: str, name: str, method: str, url: str,
                     headers: dict | None = None, body: str = "",
                     status: int = 0, response: str = "") -> SavedRequest:
        req = SavedRequest(
            request_id=f"req_{secrets.token_urlsafe(6)}",
            name=name, method=method.upper(), url=url,
            headers=headers or {}, body=body,
            response_status=status, response_body=response,
        )
        self._requests[user_id][req.request_id] = req
        return req

    def get_history(self, user_id: str, limit: int = 50) -> list[SavedRequest]:
        reqs = list(self._requests.get(user_id, {}).values())
        reqs.sort(key=lambda r: r.timestamp, reverse=True)
        return reqs[:limit]

    def create_collection(self, user_id: str, name: str,
                          description: str = "") -> Collection:
        col = Collection(
            collection_id=f"col_{secrets.token_urlsafe(6)}",
            name=name, description=description,
        )
        self._collections[user_id][col.collection_id] = col
        return col

    def add_to_collection(self, user_id: str, collection_id: str,
                          request_id: str) -> bool:
        col = self._collections.get(user_id, {}).get(collection_id)
        req = self._requests.get(user_id, {}).get(request_id)
        if col and req and request_id not in col.requests:
            col.requests.append(request_id)
            return True
        return False

    def get_collections(self, user_id: str) -> list[Collection]:
        return list(self._collections.get(user_id, {}).values())

    def delete_request(self, user_id: str, request_id: str) -> bool:
        return self._requests.get(user_id, {}).pop(request_id, None) is not None

    def search(self, user_id: str, query: str) -> list[SavedRequest]:
        q = query.lower()
        return [r for r in self._requests.get(user_id, {}).values()
                if q in r.name.lower() or q in r.url.lower()]
