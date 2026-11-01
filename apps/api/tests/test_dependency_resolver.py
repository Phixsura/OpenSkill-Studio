"""Tests for Dependency Resolver — topological sort, cycles, version constraints, conflicts."""

import pytest

from app.services.dependency_resolver import (
    DependencyResolver,
    PackageInfo,
    ResolutionStatus,
    SemVer,
    VersionConstraint,
    parse_constraint,
    parse_semver,
)


class TestSemVer:
    def test_parse_valid(self):
        v = parse_semver("1.2.3")
        assert v == SemVer(1, 2, 3)

    def test_parse_zero(self):
        v = parse_semver("0.0.0")
        assert v == SemVer(0, 0, 0)

    def test_parse_invalid(self):
        assert parse_semver("not-a-version") is None
        assert parse_semver("1.2") is None
        assert parse_semver("") is None

    def test_ordering(self):
        assert SemVer(1, 0, 0) < SemVer(2, 0, 0)
        assert SemVer(1, 1, 0) < SemVer(1, 2, 0)
        assert SemVer(1, 1, 1) < SemVer(1, 1, 2)
        assert SemVer(1, 0, 0) <= SemVer(1, 0, 0)

    def test_str(self):
        assert str(SemVer(1, 2, 3)) == "1.2.3"


class TestVersionConstraint:
    def test_exact(self):
        c = parse_constraint("=1.0.0")
        assert c is not None
        assert c.satisfies(SemVer(1, 0, 0)) is True
        assert c.satisfies(SemVer(1, 0, 1)) is False

    def test_gte(self):
        c = parse_constraint(">=1.0.0")
        assert c.satisfies(SemVer(1, 0, 0)) is True
        assert c.satisfies(SemVer(2, 0, 0)) is True
        assert c.satisfies(SemVer(0, 9, 0)) is False

    def test_lt(self):
        c = parse_constraint("<2.0.0")
        assert c.satisfies(SemVer(1, 9, 9)) is True
        assert c.satisfies(SemVer(2, 0, 0)) is False

    def test_caret(self):
        c = parse_constraint("^1.2.0")
        assert c.satisfies(SemVer(1, 2, 0)) is True
        assert c.satisfies(SemVer(1, 9, 9)) is True
        assert c.satisfies(SemVer(2, 0, 0)) is False
        assert c.satisfies(SemVer(1, 1, 0)) is False

    def test_tilde(self):
        c = parse_constraint("~1.2.0")
        assert c.satisfies(SemVer(1, 2, 0)) is True
        assert c.satisfies(SemVer(1, 2, 9)) is True
        assert c.satisfies(SemVer(1, 3, 0)) is False

    def test_bare_version_is_exact(self):
        c = parse_constraint("1.0.0")
        assert c is not None
        assert c.operator == "="
        assert c.satisfies(SemVer(1, 0, 0)) is True

    def test_invalid_constraint(self):
        assert parse_constraint("latest") is None
        assert parse_constraint("") is None


class TestDependencyResolver:
    def _setup_linear(self) -> DependencyResolver:
        """A → B → C (linear chain)"""
        r = DependencyResolver()
        r.register(PackageInfo("A", "1.0.0", {"B": ">=1.0.0"}))
        r.register(PackageInfo("B", "1.0.0", {"C": ">=1.0.0"}))
        r.register(PackageInfo("C", "1.0.0", {}))
        return r

    def _setup_diamond(self) -> DependencyResolver:
        """A → B, A → C, B → D, C → D (diamond)"""
        r = DependencyResolver()
        r.register(PackageInfo("A", "1.0.0", {"B": ">=1.0.0", "C": ">=1.0.0"}))
        r.register(PackageInfo("B", "1.0.0", {"D": ">=1.0.0"}))
        r.register(PackageInfo("C", "1.0.0", {"D": ">=1.0.0"}))
        r.register(PackageInfo("D", "1.0.0", {}))
        return r

    def test_linear_resolution(self):
        r = self._setup_linear()
        result = r.resolve(["A"])
        assert result.status == ResolutionStatus.RESOLVED
        # C must come before B, B before A
        assert result.install_order.index("C") < result.install_order.index("B")
        assert result.install_order.index("B") < result.install_order.index("A")

    def test_diamond_resolution(self):
        r = self._setup_diamond()
        result = r.resolve(["A"])
        assert result.status == ResolutionStatus.RESOLVED
        assert result.install_order.index("D") < result.install_order.index("B")
        assert result.install_order.index("D") < result.install_order.index("C")

    def test_no_deps(self):
        r = DependencyResolver()
        r.register(PackageInfo("solo", "1.0.0", {}))
        result = r.resolve(["solo"])
        assert result.status == ResolutionStatus.RESOLVED
        assert result.install_order == ["solo"]

    def test_multiple_roots(self):
        r = DependencyResolver()
        r.register(PackageInfo("X", "1.0.0", {}))
        r.register(PackageInfo("Y", "1.0.0", {}))
        result = r.resolve(["X", "Y"])
        assert result.status == ResolutionStatus.RESOLVED
        assert set(result.install_order) == {"X", "Y"}

    def test_cycle_detected(self):
        r = DependencyResolver()
        r.register(PackageInfo("A", "1.0.0", {"B": ">=1.0.0"}))
        r.register(PackageInfo("B", "1.0.0", {"C": ">=1.0.0"}))
        r.register(PackageInfo("C", "1.0.0", {"A": ">=1.0.0"}))
        result = r.resolve(["A"])
        assert result.status == ResolutionStatus.CYCLE_DETECTED
        assert result.cycle_path is not None
        assert len(result.cycle_path) >= 2

    def test_self_cycle(self):
        r = DependencyResolver()
        r.register(PackageInfo("loop", "1.0.0", {"loop": ">=1.0.0"}))
        result = r.resolve(["loop"])
        assert result.status == ResolutionStatus.CYCLE_DETECTED

    def test_missing_dependency(self):
        r = DependencyResolver()
        r.register(PackageInfo("A", "1.0.0", {"missing": ">=1.0.0"}))
        result = r.resolve(["A"])
        assert result.status == ResolutionStatus.MISSING_DEPENDENCY
        assert "missing" in result.missing

    def test_missing_root(self):
        r = DependencyResolver()
        result = r.resolve(["nonexistent"])
        assert result.status == ResolutionStatus.MISSING_DEPENDENCY

    def test_version_conflict(self):
        r = DependencyResolver()
        r.register(PackageInfo("A", "1.0.0", {"B": ">=2.0.0"}))
        r.register(PackageInfo("B", "1.5.0", {}))  # only 1.5.0 available
        result = r.resolve(["A"])
        assert result.status == ResolutionStatus.VERSION_CONFLICT
        assert len(result.conflicts) == 1
        assert "B" in result.conflicts[0]

    def test_caret_constraint_satisfied(self):
        r = DependencyResolver()
        r.register(PackageInfo("A", "1.0.0", {"B": "^1.0.0"}))
        r.register(PackageInfo("B", "1.5.0", {}))
        result = r.resolve(["A"])
        assert result.status == ResolutionStatus.RESOLVED

    def test_caret_constraint_rejected(self):
        r = DependencyResolver()
        r.register(PackageInfo("A", "1.0.0", {"B": "^1.0.0"}))
        r.register(PackageInfo("B", "2.0.0", {}))
        result = r.resolve(["A"])
        assert result.status == ResolutionStatus.VERSION_CONFLICT


class TestBuildTree:
    def test_single_node(self):
        r = DependencyResolver()
        r.register(PackageInfo("root", "1.0.0", {}))
        tree = r.build_tree("root")
        assert tree is not None
        assert tree.name == "root"
        assert tree.children == []

    def test_tree_structure(self):
        r = DependencyResolver()
        r.register(PackageInfo("app", "2.0.0", {"lib": ">=1.0.0"}))
        r.register(PackageInfo("lib", "1.0.0", {"core": ">=0.5.0"}))
        r.register(PackageInfo("core", "0.5.0", {}))
        tree = r.build_tree("app")
        assert tree is not None
        assert len(tree.children) == 1
        assert tree.children[0].name == "lib"
        assert len(tree.children[0].children) == 1
        assert tree.children[0].children[0].name == "core"

    def test_unknown_root_returns_none(self):
        r = DependencyResolver()
        assert r.build_tree("nonexistent") is None

    def test_max_depth(self):
        r = DependencyResolver()
        r.register(PackageInfo("a", "1.0.0", {"b": ">=1.0.0"}))
        r.register(PackageInfo("b", "1.0.0", {"c": ">=1.0.0"}))
        r.register(PackageInfo("c", "1.0.0", {}))
        tree = r.build_tree("a", max_depth=1)
        assert tree is not None
        assert len(tree.children) == 1
        # Depth-limited: b's children not expanded
        assert tree.children[0].children == []

    def test_diamond_no_duplicate_traversal(self):
        r = DependencyResolver()
        r.register(PackageInfo("root", "1.0.0", {"left": ">=1.0.0", "right": ">=1.0.0"}))
        r.register(PackageInfo("left", "1.0.0", {"shared": ">=1.0.0"}))
        r.register(PackageInfo("right", "1.0.0", {"shared": ">=1.0.0"}))
        r.register(PackageInfo("shared", "1.0.0", {}))
        tree = r.build_tree("root")
        assert tree is not None
        assert len(tree.children) == 2
