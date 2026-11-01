"""Webhook retry manager — manage failed webhook delivery retries."""
from __future__ import annotations
import time


def create_retry_queue(webhook_id: str, url: str, payload: str,
                        max_retries: int = 5) -> dict:
    return {"webhook_id": webhook_id, "url": url, "payload_size": len(payload),
            "max_retries": max_retries, "attempts": 0, "status": "pending",
            "next_retry_at": time.time(), "created_at": time.time()}


def attempt_retry(entry: dict, success: bool) -> dict:
    entry["attempts"] += 1
    if success:
        entry["status"] = "delivered"
        return {"delivered": True, "attempts": entry["attempts"]}
    if entry["attempts"] >= entry["max_retries"]:
        entry["status"] = "failed"
        return {"delivered": False, "exhausted": True, "attempts": entry["attempts"]}
    delay = min(60 * (2 ** entry["attempts"]), 3600)  # exponential backoff, max 1hr
    entry["next_retry_at"] = time.time() + delay
    entry["status"] = "retrying"
    return {"delivered": False, "exhausted": False, "next_delay_sec": delay,
            "attempts": entry["attempts"]}


def retry_stats(queue: list[dict]) -> dict:
    pending = sum(1 for e in queue if e["status"] == "pending")
    retrying = sum(1 for e in queue if e["status"] == "retrying")
    delivered = sum(1 for e in queue if e["status"] == "delivered")
    failed = sum(1 for e in queue if e["status"] == "failed")
    return {"total": len(queue), "pending": pending, "retrying": retrying,
            "delivered": delivered, "failed": failed,
            "delivery_rate": round(delivered / max(len(queue), 1) * 100)}
