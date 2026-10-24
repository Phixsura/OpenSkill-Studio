"""Fleet webhook delivery — track webhook delivery success rates."""
from __future__ import annotations
def fleet_webhook_delivery(endpoints: list[dict]) -> dict:
    delivered = sum(e.get("delivered", 0) for e in endpoints)
    failed = sum(e.get("failed", 0) for e in endpoints)
    total = delivered + failed
    rate = round(delivered / max(total, 1) * 100, 1)
    return {"delivered": delivered, "failed": failed, "success_rate": rate, "reliable": rate >= 99}
