"""Developer playground v2 — enhanced playground with environment presets and sharing."""

import hashlib
from datetime import datetime, timezone


def create_playground_v2(*, developer_id: str, app_id: str, preset: str = "default") -> dict:
    presets = {
        "default": {"timeout_ms": 5000, "max_memory_mb": 128, "network": True},
        "minimal": {"timeout_ms": 2000, "max_memory_mb": 64, "network": False},
        "full": {"timeout_ms": 30000, "max_memory_mb": 512, "network": True},
    }
    config = presets.get(preset, presets["default"])
    share_id = hashlib.sha256(f"{developer_id}:{app_id}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:10]
    return {"developer_id": developer_id, "app_id": app_id, "preset": preset,
            "config": config, "share_id": share_id, "status": "active"}


def fork_playground(*, source_share_id: str, developer_id: str) -> dict:
    return {"forked_from": source_share_id, "developer_id": developer_id,
            "status": "active", "is_fork": True}


def export_playground(*, playground: dict, format: str = "json") -> dict:
    return {"share_id": playground.get("share_id"), "format": format,
            "config": playground.get("config"), "exportable": True}
