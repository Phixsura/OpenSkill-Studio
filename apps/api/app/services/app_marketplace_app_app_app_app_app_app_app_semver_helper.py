"""Semantic versioning helper — parse, compare, bump versions."""
from __future__ import annotations
import re

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-(.+))?$")


def parse_version(version: str) -> dict:
    m = SEMVER_RE.match(version)
    if not m:
        return {"valid": False, "error": "invalid_semver"}
    return {"valid": True, "major": int(m.group(1)), "minor": int(m.group(2)),
            "patch": int(m.group(3)), "prerelease": m.group(4) or "",
            "is_prerelease": m.group(4) is not None}


def bump(version: str, bump_type: str) -> dict:
    p = parse_version(version)
    if not p["valid"]:
        return p
    if bump_type == "major":
        return {"version": f"{p['major']+1}.0.0", "bump": "major"}
    elif bump_type == "minor":
        return {"version": f"{p['major']}.{p['minor']+1}.0", "bump": "minor"}
    elif bump_type == "patch":
        return {"version": f"{p['major']}.{p['minor']}.{p['patch']+1}", "bump": "patch"}
    return {"error": "invalid_bump_type"}


def compare(a: str, b: str) -> dict:
    pa, pb = parse_version(a), parse_version(b)
    if not pa["valid"] or not pb["valid"]:
        return {"error": "invalid_version"}
    for field in ("major", "minor", "patch"):
        if pa[field] > pb[field]:
            return {"result": 1, "newer": a, "comparison": f"{a} > {b}"}
        if pa[field] < pb[field]:
            return {"result": -1, "newer": b, "comparison": f"{a} < {b}"}
    return {"result": 0, "newer": None, "comparison": f"{a} == {b}"}
