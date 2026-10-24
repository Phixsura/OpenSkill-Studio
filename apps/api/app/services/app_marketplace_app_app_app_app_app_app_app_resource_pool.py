"""Resource pool manager — manage shared resource pools with allocation."""
from __future__ import annotations


class ResourcePool:
    def __init__(self, name: str, capacity: int):
        self.name = name
        self.capacity = capacity
        self._allocated: dict[str, int] = {}

    def allocate(self, owner: str, amount: int) -> dict:
        used = sum(self._allocated.values())
        available = self.capacity - used
        if amount > available:
            return {"success": False, "owner": owner, "requested": amount,
                    "available": available, "reason": "insufficient_capacity"}
        self._allocated[owner] = self._allocated.get(owner, 0) + amount
        return {"success": True, "owner": owner, "allocated": amount,
                "total_owned": self._allocated[owner], "remaining": available - amount}

    def release(self, owner: str, amount: int) -> dict:
        current = self._allocated.get(owner, 0)
        released = min(amount, current)
        self._allocated[owner] = current - released
        if self._allocated[owner] <= 0:
            del self._allocated[owner]
        return {"owner": owner, "released": released, "remaining_owned": self._allocated.get(owner, 0)}

    def status(self) -> dict:
        used = sum(self._allocated.values())
        return {"pool": self.name, "capacity": self.capacity, "used": used,
                "available": self.capacity - used,
                "utilization_pct": round(used / max(self.capacity, 1) * 100, 1),
                "owners": len(self._allocated)}
