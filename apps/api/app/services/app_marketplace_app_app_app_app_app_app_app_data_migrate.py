"""Data migration planner — plan and track data migrations."""
from __future__ import annotations


def plan_migration(source: dict, target: dict, tables: list[dict]) -> dict:
    steps = []
    total_rows = 0
    for t in tables:
        rows = t.get("row_count", 0)
        total_rows += rows
        est_minutes = round(rows / max(t.get("throughput", 10000), 1), 1)
        steps.append({"table": t["name"], "rows": rows,
                      "estimated_minutes": est_minutes,
                      "strategy": "bulk" if rows > 100000 else "streaming"})
    steps.sort(key=lambda s: -s["rows"])
    total_minutes = sum(s["estimated_minutes"] for s in steps)
    return {"source": source.get("name", ""), "target": target.get("name", ""),
            "steps": steps, "total_rows": total_rows,
            "total_tables": len(tables),
            "estimated_minutes": round(total_minutes, 1)}


def validate_migration(before: dict, after: dict) -> dict:
    mismatches = []
    for table, count in before.items():
        actual = after.get(table, 0)
        if actual != count:
            mismatches.append({"table": table, "expected": count,
                               "actual": actual, "diff": actual - count})
    return {"valid": len(mismatches) == 0, "tables_checked": len(before),
            "mismatches": mismatches}
