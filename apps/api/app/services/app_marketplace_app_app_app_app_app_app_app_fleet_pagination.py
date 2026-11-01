"""Fleet API pagination — track pagination adoption."""
from __future__ import annotations
def fleet_pagination(endpoints: list[dict]) -> dict:
    paginated = [e for e in endpoints if e.get("supports_pagination", False)]
    cursor_based = [e for e in endpoints if e.get("pagination_type") == "cursor"]
    return {"total": len(endpoints), "paginated": len(paginated),
            "cursor_based": len(cursor_based), "unpaginated": len(endpoints) - len(paginated)}
