"""Platform API changelog — track breaking and non-breaking API changes."""
from __future__ import annotations

def generate_api_changelog(changes: list[dict]) -> dict:
    breaking = [c for c in changes if c.get("breaking")]
    non_breaking = [c for c in changes if not c.get("breaking")]
    return {"total": len(changes), "breaking": len(breaking),
            "non_breaking": len(non_breaking),
            "changes": changes, "has_breaking": len(breaking) > 0}
