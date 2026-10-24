"""App dependency update — dependency update advisor with risk assessment."""

import html
import re

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)")


def check_updates(*, dependencies: list[dict]) -> dict:
    items = []
    updates_available = 0
    breaking = 0
    for dep in dependencies:
        current = dep.get("current", "0.0.0")
        latest = dep.get("latest", current)
        cm = SEMVER_RE.match(current)
        lm = SEMVER_RE.match(latest)
        needs_update = current != latest
        update_type = None
        if needs_update and cm and lm:
            updates_available += 1
            if int(lm.group(1)) > int(cm.group(1)):
                update_type = "major"
                breaking += 1
            elif int(lm.group(2)) > int(cm.group(2)):
                update_type = "minor"
            else:
                update_type = "patch"
        items.append({
            "name": html.escape(dep.get("name", "")),
            "current": current, "latest": latest,
            "needs_update": needs_update, "update_type": update_type,
            "is_breaking": update_type == "major",
        })
    items.sort(key=lambda x: (0 if x.get("is_breaking") else 1, x["name"]))
    return {"dependencies": items, "total": len(items),
            "updates_available": updates_available, "breaking": breaking,
            "up_to_date": updates_available == 0}
