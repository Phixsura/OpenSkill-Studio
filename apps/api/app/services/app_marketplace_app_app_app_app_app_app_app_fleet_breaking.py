"""Fleet breaking change — detect breaking API changes."""
from __future__ import annotations
def fleet_breaking_changes(changes: list[dict]) -> dict:
    breaking = [c for c in changes if c.get("breaking", False)]
    with_migration = [c for c in breaking if c.get("has_migration_guide", False)]
    return {"total_changes": len(changes), "breaking": len(breaking),
            "with_guide": len(with_migration), "safe": len(breaking) == 0}
