"""Fleet changelog — auto-generate platform changelog stats."""
from __future__ import annotations
def fleet_changelog(entries: list[dict]) -> dict:
    features = [e for e in entries if e.get("type") == "feat"]
    fixes = [e for e in entries if e.get("type") == "fix"]
    breaking = [e for e in entries if e.get("breaking", False)]
    return {"total": len(entries), "features": len(features), "fixes": len(fixes),
            "breaking": len(breaking), "semver_bump": "major" if breaking else ("minor" if features else "patch")}
