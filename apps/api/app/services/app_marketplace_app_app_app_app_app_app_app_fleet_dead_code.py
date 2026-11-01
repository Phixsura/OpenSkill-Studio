"""Fleet dead code — detect unused code across the platform."""
from __future__ import annotations
def fleet_dead_code(files: list[dict]) -> dict:
    unused = [f for f in files if f.get("references", 1) == 0]
    total_loc = sum(f.get("lines", 0) for f in unused)
    return {"total_files": len(files), "dead_files": len(unused),
            "dead_loc": total_loc, "clean": len(unused) == 0}
