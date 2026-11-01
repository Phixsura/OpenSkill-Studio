"""App version selector — version picker with compatibility info."""

import html
import re

SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)")


def build_version_selector(*, versions: list[dict], current: str = "",
                              min_compatible: str | None = None) -> dict:
    items = []
    for v in sorted(versions, key=lambda x: x.get("published_at", ""), reverse=True):
        ver = v["version"]
        is_current = ver == current
        is_prerelease = "-" in ver
        compatible = True
        if min_compatible:
            mc = SEMVER_RE.match(min_compatible)
            vc = SEMVER_RE.match(ver)
            if mc and vc:
                compatible = (int(vc.group(1)), int(vc.group(2)), int(vc.group(3))) >= \
                             (int(mc.group(1)), int(mc.group(2)), int(mc.group(3)))
        items.append({
            "version": ver, "published_at": v.get("published_at", ""),
            "is_current": is_current, "is_prerelease": is_prerelease,
            "compatible": compatible, "downloads": v.get("downloads", 0),
        })
    return {"versions": items, "total": len(items), "current": current,
            "latest_stable": next((v["version"] for v in items if not v["is_prerelease"]), None)}
