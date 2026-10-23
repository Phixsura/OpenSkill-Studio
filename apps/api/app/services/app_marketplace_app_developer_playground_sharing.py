"""Playground sharing — share playground configs and snippets with other developers."""

import hashlib
from datetime import datetime, timezone


def create_shared_snippet(*, developer_id: str, code: str, language: str,
                            title: str, description: str = "") -> dict:
    snippet_id = hashlib.sha256(f"{developer_id}:{code}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:10]
    return {"snippet_id": snippet_id, "developer_id": developer_id, "title": title,
            "description": description, "language": language, "code": code,
            "views": 0, "forks": 0, "created_at": datetime.now(timezone.utc).isoformat()}


def fork_snippet(*, snippet: dict, developer_id: str) -> dict:
    return {**snippet, "developer_id": developer_id, "forked_from": snippet["snippet_id"],
            "forks": 0, "views": 0}


def get_trending_snippets(*, snippets: list[dict], limit: int = 10) -> list[dict]:
    scored = sorted(snippets, key=lambda s: s.get("views", 0) * 0.3 + s.get("forks", 0) * 0.7, reverse=True)
    return scored[:limit]
