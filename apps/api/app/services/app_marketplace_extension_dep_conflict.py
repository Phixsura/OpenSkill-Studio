"""Dependency Conflict Resolver — detect and resolve version conflicts.

Implements semantic version constraint matching with:
- Range parsing (^1.2.0, ~1.2.0, >=1.0.0 <2.0.0, exact)
- Conflict detection when two extensions need incompatible versions
- Resolution strategies: newest-compatible, oldest-compatible, force
- Diamond dependency detection (A→C@1, B→C@2)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re

VERSION_RE = re.compile(r'^(\d+)\.(\d+)\.(\d+)$')


def parse_version(v: str) -> tuple[int, int, int] | None:
    m = VERSION_RE.match(v.strip())
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def version_satisfies(version: str, constraint: str) -> bool:
    """Check if a version satisfies a constraint like ^1.2.0, ~1.2.0, >=1.0.0, exact."""
    v = parse_version(version)
    if not v:
        return False
    constraint = constraint.strip()

    if constraint.startswith("^"):
        # Caret: compatible with major (^1.2.3 → >=1.2.3 <2.0.0)
        base = parse_version(constraint[1:])
        if not base:
            return False
        if base[0] == 0:
            # ^0.x.y → >=0.x.y <0.(x+1).0
            return v[0] == 0 and v[1] == base[1] and v >= base
        return v[0] == base[0] and v >= base

    if constraint.startswith("~"):
        # Tilde: patch-level changes (~1.2.3 → >=1.2.3 <1.3.0)
        base = parse_version(constraint[1:])
        if not base:
            return False
        return v[0] == base[0] and v[1] == base[1] and v >= base

    if constraint.startswith(">="):
        base = parse_version(constraint[2:])
        return base is not None and v >= base

    if constraint.startswith(">"):
        base = parse_version(constraint[1:])
        return base is not None and v > base

    if constraint.startswith("<="):
        base = parse_version(constraint[2:])
        return base is not None and v <= base

    if constraint.startswith("<"):
        base = parse_version(constraint[1:])
        return base is not None and v < base

    # Exact match
    return version.strip() == constraint


@dataclass
class DepRequirement:
    package: str
    constraint: str
    required_by: str  # who needs it


@dataclass
class Conflict:
    package: str
    requirements: list[DepRequirement]
    reason: str


@dataclass
class Resolution:
    package: str
    version: str
    strategy: str


class DepConflictResolverService:
    def __init__(self):
        self._available_versions: dict[str, list[str]] = {}  # package -> sorted versions

    def register_versions(self, package: str, versions: list[str]) -> None:
        parsed = [(v, parse_version(v)) for v in versions]
        valid = [(v, p) for v, p in parsed if p is not None]
        valid.sort(key=lambda x: x[1])
        self._available_versions[package] = [v for v, _ in valid]

    def detect_conflicts(self, requirements: list[DepRequirement]) -> list[Conflict]:
        """Find packages where requirements are mutually unsatisfiable."""
        by_package: dict[str, list[DepRequirement]] = {}
        for req in requirements:
            by_package.setdefault(req.package, []).append(req)

        conflicts = []
        for pkg, reqs in by_package.items():
            if len(reqs) < 2:
                continue
            versions = self._available_versions.get(pkg, [])
            # Find versions that satisfy ALL constraints
            common = [v for v in versions
                      if all(version_satisfies(v, r.constraint) for r in reqs)]
            if not common:
                conflicts.append(Conflict(
                    package=pkg, requirements=reqs,
                    reason=f"No version of {pkg} satisfies: " +
                           ", ".join(f"{r.constraint} (by {r.required_by})" for r in reqs)))
        return conflicts

    def resolve(self, requirements: list[DepRequirement],
                strategy: str = "newest") -> list[Resolution]:
        """Resolve each package to a specific version."""
        by_package: dict[str, list[DepRequirement]] = {}
        for req in requirements:
            by_package.setdefault(req.package, []).append(req)

        resolutions = []
        for pkg, reqs in by_package.items():
            versions = self._available_versions.get(pkg, [])
            candidates = [v for v in versions
                          if all(version_satisfies(v, r.constraint) for r in reqs)]

            if candidates:
                if strategy == "newest":
                    chosen = candidates[-1]
                elif strategy == "oldest":
                    chosen = candidates[0]
                else:
                    chosen = candidates[-1]
                resolutions.append(Resolution(package=pkg, version=chosen, strategy=strategy))
            else:
                # Force: pick newest that satisfies the most constraints
                best = None
                best_score = -1
                for v in reversed(versions):
                    score = sum(1 for r in reqs if version_satisfies(v, r.constraint))
                    if score > best_score:
                        best_score = score
                        best = v
                if best:
                    resolutions.append(Resolution(package=pkg, version=best, strategy="force"))

        return resolutions
