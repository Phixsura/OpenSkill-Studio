"""Dependency Resolver — topological ordering and conflict detection for pack/app dependencies.

Resolves dependency graphs for skill packs, workflow packs, and developer apps:
- Topological sort for install ordering
- Cycle detection with path reporting
- Version constraint satisfaction (semver ranges)
- Conflict detection (incompatible version requirements)
- Missing dependency identification
- Dependency tree visualization
"""

from __future__ import annotations

import re
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()

# Simplified semver: major.minor.patch
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


class ResolutionStatus(str, Enum):
    RESOLVED = "resolved"
    CYCLE_DETECTED = "cycle_detected"
    MISSING_DEPENDENCY = "missing_dependency"
    VERSION_CONFLICT = "version_conflict"


@dataclass(frozen=True)
class SemVer:
    """Parsed semantic version."""

    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: SemVer) -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __le__(self, other: SemVer) -> bool:
        return (self.major, self.minor, self.patch) <= (other.major, other.minor, other.patch)


def parse_semver(version: str) -> SemVer | None:
    """Parse a semver string. Returns None if invalid."""
    m = SEMVER_RE.match(version.strip())
    if not m:
        return None
    return SemVer(int(m.group(1)), int(m.group(2)), int(m.group(3)))


@dataclass
class VersionConstraint:
    """A version constraint like >=1.0.0, <2.0.0, ^1.2.0, =1.0.0."""

    raw: str
    operator: str  # >=, <=, >, <, =, ^, ~
    version: SemVer

    def satisfies(self, candidate: SemVer) -> bool:
        if self.operator == "=":
            return candidate == self.version
        elif self.operator == ">=":
            return candidate >= self.version
        elif self.operator == "<=":
            return candidate <= self.version
        elif self.operator == ">":
            return not (candidate <= self.version)
        elif self.operator == "<":
            return candidate < self.version
        elif self.operator == "^":
            # ^1.2.3 means >=1.2.3, <2.0.0 (compatible with major)
            if candidate < self.version:
                return False
            return candidate.major == self.version.major
        elif self.operator == "~":
            # ~1.2.3 means >=1.2.3, <1.3.0 (compatible with minor)
            if candidate < self.version:
                return False
            return (candidate.major == self.version.major
                    and candidate.minor == self.version.minor)
        return False


CONSTRAINT_RE = re.compile(r"^(\^|~|>=|<=|>|<|=)?(\d+\.\d+\.\d+)$")


def parse_constraint(raw: str) -> VersionConstraint | None:
    """Parse a version constraint string."""
    m = CONSTRAINT_RE.match(raw.strip())
    if not m:
        return None
    op = m.group(1) or "="
    ver = parse_semver(m.group(2))
    if ver is None:
        return None
    return VersionConstraint(raw=raw.strip(), operator=op, version=ver)


@dataclass
class PackageInfo:
    """A package (pack or app) with its version and dependencies."""

    name: str
    version: str
    dependencies: dict[str, str] = field(default_factory=dict)
    # name → version constraint string, e.g. {"react-pack": "^2.0.0"}


@dataclass
class ResolutionResult:
    """Result of resolving a dependency graph."""

    status: ResolutionStatus
    install_order: list[str]  # topologically sorted package names
    errors: list[str]
    cycle_path: list[str] | None = None
    missing: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)


@dataclass
class DependencyNode:
    """A node in the dependency tree."""

    name: str
    version: str
    depth: int
    children: list[DependencyNode] = field(default_factory=list)


class DependencyResolver:
    """Resolve dependency graphs with version constraints."""

    def __init__(self):
        # name → PackageInfo (latest or only registered version)
        self._registry: dict[str, PackageInfo] = {}
        # name → list of all versions
        self._versions: dict[str, list[PackageInfo]] = defaultdict(list)

    def register(self, package: PackageInfo) -> None:
        """Register a package in the resolver's registry."""
        self._registry[package.name] = package
        self._versions[package.name].append(package)

    def resolve(self, root_names: list[str]) -> ResolutionResult:
        """Resolve dependencies for a set of root packages.

        Returns a topologically sorted install order, or errors.
        """
        # 1. Collect all transitive dependencies
        all_deps: dict[str, set[str]] = {}  # name → set of dependency names
        visited: set[str] = set()
        missing: list[str] = []
        conflicts: list[str] = []

        def collect(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            pkg = self._registry.get(name)
            if pkg is None:
                missing.append(name)
                return
            deps = set()
            for dep_name, constraint_str in pkg.dependencies.items():
                deps.add(dep_name)
                # Check version constraint satisfaction
                dep_pkg = self._registry.get(dep_name)
                if dep_pkg is None:
                    missing.append(dep_name)
                    continue
                constraint = parse_constraint(constraint_str)
                if constraint:
                    dep_ver = parse_semver(dep_pkg.version)
                    if dep_ver and not constraint.satisfies(dep_ver):
                        conflicts.append(
                            f"{name} requires {dep_name} {constraint_str}, "
                            f"but {dep_ver} is available"
                        )
                collect(dep_name)
            all_deps[name] = deps

        for name in root_names:
            collect(name)

        if missing:
            return ResolutionResult(
                status=ResolutionStatus.MISSING_DEPENDENCY,
                install_order=[],
                errors=[f"Missing package: {m}" for m in missing],
                missing=missing,
            )

        if conflicts:
            return ResolutionResult(
                status=ResolutionStatus.VERSION_CONFLICT,
                install_order=[],
                errors=conflicts,
                conflicts=conflicts,
            )

        # 2. Detect cycles
        cycle = self._detect_cycle(all_deps)
        if cycle:
            return ResolutionResult(
                status=ResolutionStatus.CYCLE_DETECTED,
                install_order=[],
                errors=[f"Dependency cycle: {' → '.join(cycle)}"],
                cycle_path=cycle,
            )

        # 3. Topological sort (Kahn's algorithm)
        order = self._topological_sort(all_deps)

        return ResolutionResult(
            status=ResolutionStatus.RESOLVED,
            install_order=order,
            errors=[],
        )

    def build_tree(self, root_name: str, max_depth: int = 10) -> DependencyNode | None:
        """Build a dependency tree for visualization."""
        pkg = self._registry.get(root_name)
        if pkg is None:
            return None
        return self._build_node(pkg, depth=0, max_depth=max_depth, seen=set())

    # ── Internals ────────────────────────────────────────

    def _detect_cycle(self, graph: dict[str, set[str]]) -> list[str] | None:
        """Detect cycles using DFS coloring. Returns cycle path or None."""
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = {n: WHITE for n in graph}
        parent: dict[str, str | None] = {n: None for n in graph}

        def dfs(node: str) -> list[str] | None:
            color[node] = GRAY
            for neighbor in graph.get(node, set()):
                if neighbor not in color:
                    continue
                if color[neighbor] == GRAY:
                    # Found cycle — reconstruct path
                    path = [neighbor, node]
                    current = node
                    while parent[current] is not None and parent[current] != neighbor:
                        current = parent[current]  # type: ignore[assignment]
                        path.append(current)
                    path.reverse()
                    return path
                if color[neighbor] == WHITE:
                    parent[neighbor] = node
                    result = dfs(neighbor)
                    if result:
                        return result
            color[node] = BLACK
            return None

        for node in graph:
            if color[node] == WHITE:
                result = dfs(node)
                if result:
                    return result
        return None

    @staticmethod
    def _topological_sort(graph: dict[str, set[str]]) -> list[str]:
        """Kahn's algorithm for topological ordering."""
        in_degree: dict[str, int] = defaultdict(int)
        for node in graph:
            in_degree.setdefault(node, 0)
            for dep in graph[node]:
                in_degree[dep] = in_degree.get(dep, 0) + 1

        queue = deque(sorted(n for n, d in in_degree.items() if d == 0))
        order: list[str] = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for dep in sorted(graph.get(node, set())):
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)

        # Reverse: dependencies first, then dependents
        order.reverse()
        return order

    def _build_node(self, pkg: PackageInfo, depth: int,
                    max_depth: int, seen: set[str]) -> DependencyNode:
        node = DependencyNode(name=pkg.name, version=pkg.version, depth=depth)
        if depth >= max_depth or pkg.name in seen:
            return node
        seen = seen | {pkg.name}
        for dep_name in sorted(pkg.dependencies):
            dep_pkg = self._registry.get(dep_name)
            if dep_pkg:
                child = self._build_node(dep_pkg, depth + 1, max_depth, seen)
                node.children.append(child)
        return node
