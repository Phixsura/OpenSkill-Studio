"""Fleet code ownership — track CODEOWNERS coverage."""
from __future__ import annotations
def fleet_code_ownership(files: list[dict]) -> dict:
    owned = [f for f in files if f.get("has_owner", False)]
    unowned = len(files) - len(owned)
    pct = round(len(owned) / max(len(files), 1) * 100, 1)
    return {"total": len(files), "owned": len(owned), "unowned": unowned,
            "coverage_pct": pct, "full_coverage": unowned == 0}
