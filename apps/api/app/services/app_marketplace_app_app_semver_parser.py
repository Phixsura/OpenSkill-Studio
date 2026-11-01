"""Semver parser — semantic version parsing and comparison."""

import re

SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.]+))?(?:\+([a-zA-Z0-9.]+))?$")


def parse_semver(*, version: str) -> dict:
    m = SEMVER_RE.match(version.strip())
    if not m:
        return {"valid": False, "error": f"Invalid semver: {version}"}
    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))
    pre = m.group(4)
    build = m.group(5)
    return {"valid": True, "major": major, "minor": minor, "patch": patch,
            "prerelease": pre, "build": build,
            "is_stable": pre is None, "normalized": f"{major}.{minor}.{patch}"}


def compare_versions(*, v1: str, v2: str) -> dict:
    a = parse_semver(version=v1)
    b = parse_semver(version=v2)
    if not a["valid"] or not b["valid"]:
        return {"error": "Invalid version(s)"}
    for key in ("major", "minor", "patch"):
        if a[key] != b[key]:
            result = 1 if a[key] > b[key] else -1
            return {"v1": v1, "v2": v2, "result": result,
                    "newer": v1 if result > 0 else v2}
    return {"v1": v1, "v2": v2, "result": 0, "newer": None}


def bump_version(*, version: str, bump: str = "patch") -> dict:
    v = parse_semver(version=version)
    if not v["valid"]:
        return v
    major, minor, patch = v["major"], v["minor"], v["patch"]
    if bump == "major":
        return {"version": f"{major+1}.0.0", "bump": bump}
    elif bump == "minor":
        return {"version": f"{major}.{minor+1}.0", "bump": bump}
    return {"version": f"{major}.{minor}.{patch+1}", "bump": bump}
