"""Mock data generator — generate realistic test data for APIs."""
from __future__ import annotations
import hashlib, secrets


def generate_users(count: int, seed: str = "default") -> list[dict]:
    users = []
    for i in range(count):
        uid = hashlib.md5(f"{seed}:{i}".encode()).hexdigest()[:8]
        users.append({"id": f"usr_{uid}", "name": f"User {i+1}",
                       "email": f"user{i+1}@example.com", "active": i % 10 != 0})
    return users


def generate_orders(count: int, user_ids: list[str]) -> list[dict]:
    orders = []
    for i in range(count):
        oid = hashlib.md5(f"order:{i}".encode()).hexdigest()[:8]
        uid = user_ids[i % len(user_ids)] if user_ids else "unknown"
        amount = round((i * 17 + 3) % 500 + 10, 2)
        orders.append({"id": f"ord_{oid}", "user_id": uid, "amount": amount,
                        "status": "completed" if i % 3 != 0 else "pending"})
    return orders


def data_stats(data: list[dict]) -> dict:
    return {"count": len(data), "fields": sorted(data[0].keys()) if data else [],
            "sample": data[0] if data else {}}
