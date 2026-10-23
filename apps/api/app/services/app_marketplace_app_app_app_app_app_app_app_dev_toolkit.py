"""Developer toolkit — collection of developer utilities and helpers."""
from __future__ import annotations
import secrets
import hashlib
import json


def generate_test_data(*, entity: str, count: int = 5) -> list[dict]:
    entities = {
        "users": lambda i: {"id": f"user_{secrets.token_hex(4)}", "name": f"User {i}", "email": f"user{i}@test.com"},
        "apps": lambda i: {"id": f"app_{secrets.token_hex(4)}", "name": f"Test App {i}", "version": f"1.{i}.0"},
        "webhooks": lambda i: {"id": f"wh_{secrets.token_hex(4)}", "url": f"https://example.com/hook{i}", "events": ["app.installed"]},
    }
    generator = entities.get(entity, entities["users"])
    return [generator(i) for i in range(1, count + 1)]


def compute_checksum(data: dict) -> str:
    serialized = json.dumps(data, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()[:16]


def format_json(data: dict, *, indent: int = 2) -> dict:
    formatted = json.dumps(data, indent=indent, sort_keys=True)
    return {"formatted": formatted, "size_bytes": len(formatted.encode()),
            "lines": formatted.count("\n") + 1}
