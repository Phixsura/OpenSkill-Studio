"""CORS policy manager — configure and validate Cross-Origin Resource Sharing."""
from __future__ import annotations
from urllib.parse import urlparse


class CorsManager:
    def __init__(self):
        self._origins: list[str] = []
        self._methods: list[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        self._headers: list[str] = ["Content-Type", "Authorization"]
        self._max_age: int = 86400
        self._credentials: bool = True

    def add_origin(self, origin: str) -> dict:
        parsed = urlparse(origin)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return {"error": f"Invalid origin: {origin}"}
        normalized = f"{parsed.scheme}://{parsed.netloc}"
        if normalized not in self._origins:
            self._origins.append(normalized)
        return {"added": normalized, "total_origins": len(self._origins)}

    def remove_origin(self, origin: str) -> dict:
        if origin in self._origins:
            self._origins.remove(origin)
            return {"removed": True}
        return {"removed": False, "reason": "not_found"}

    def check_origin(self, origin: str) -> dict:
        allowed = origin in self._origins or "*" in self._origins
        return {"origin": origin, "allowed": allowed,
                "methods": self._methods if allowed else [],
                "headers": self._headers if allowed else []}

    def policy(self) -> dict:
        return {"origins": self._origins, "methods": self._methods,
                "headers": self._headers, "max_age": self._max_age,
                "credentials": self._credentials}
