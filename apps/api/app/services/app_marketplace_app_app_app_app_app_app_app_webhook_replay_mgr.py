"""Webhook replay manager — replay failed webhooks with retry logic."""
from __future__ import annotations
import time
import hashlib


def create_replay(webhook_id: str, endpoint: str, payload: str,
                   original_status: int, max_retries: int = 3) -> dict:
    replay_id = hashlib.sha256(f"{webhook_id}:{time.time()}".encode()).hexdigest()[:10]
    return {"replay_id": replay_id, "webhook_id": webhook_id, "endpoint": endpoint,
            "payload_size": len(payload), "original_status": original_status,
            "max_retries": max_retries, "attempts": 0, "status": "pending"}


def attempt_replay(replay: dict, success: bool) -> dict:
    replay["attempts"] += 1
    if success:
        replay["status"] = "delivered"
        return {"delivered": True, "attempts": replay["attempts"]}
    if replay["attempts"] >= replay["max_retries"]:
        replay["status"] = "exhausted"
        return {"delivered": False, "exhausted": True, "attempts": replay["attempts"]}
    delay = min(60 * (2 ** replay["attempts"]), 3600)
    replay["status"] = "retrying"
    return {"delivered": False, "exhausted": False, "next_delay_sec": delay}


def replay_stats(replays: list[dict]) -> dict:
    delivered = sum(1 for r in replays if r["status"] == "delivered")
    exhausted = sum(1 for r in replays if r["status"] == "exhausted")
    pending = sum(1 for r in replays if r["status"] in ("pending", "retrying"))
    return {"total": len(replays), "delivered": delivered, "exhausted": exhausted,
            "pending": pending, "delivery_rate": round(delivered / max(len(replays), 1) * 100)}
