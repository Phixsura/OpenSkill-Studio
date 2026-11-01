"""Fleet SLSA — track Supply-chain Levels for Software Artifacts."""
from __future__ import annotations
def fleet_slsa_status(builds: list[dict]) -> dict:
    levels = {0: 0, 1: 0, 2: 0, 3: 0}
    for b in builds:
        lvl = b.get("slsa_level", 0)
        levels[lvl] = levels.get(lvl, 0) + 1
    avg_level = round(sum(b.get("slsa_level", 0) for b in builds) / max(len(builds), 1), 1)
    return {"total": len(builds), "by_level": levels, "avg_level": avg_level,
            "mature": avg_level >= 2}
