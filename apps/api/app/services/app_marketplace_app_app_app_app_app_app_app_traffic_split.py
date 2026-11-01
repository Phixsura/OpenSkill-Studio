"""Traffic split controller — split traffic between versions by percentage."""
from __future__ import annotations
import hashlib


def split_traffic(user_id: str, splits: list[dict]) -> dict:
    h = int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16) % 100
    cumulative = 0
    for split in splits:
        cumulative += split["pct"]
        if h < cumulative:
            return {"user_id": user_id, "version": split["version"],
                    "bucket": h, "split_pct": split["pct"]}
    return {"user_id": user_id, "version": splits[-1]["version"],
            "bucket": h, "split_pct": splits[-1]["pct"]}


def validate_splits(splits: list[dict]) -> dict:
    total = sum(s["pct"] for s in splits)
    valid = total == 100
    return {"valid": valid, "total_pct": total, "versions": len(splits)}
