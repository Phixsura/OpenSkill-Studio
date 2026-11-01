"""Tests for App Compatibility Matrix — declarations, impact analysis, upgrade paths."""

import pytest

from app.services.app_compatibility_matrix import (
    AppCompatibilityMatrix,
    CompatStatus,
)


def _setup() -> AppCompatibilityMatrix:
    m = AppCompatibilityMatrix()
    m.declare("app-1", "1.0.0", "2.0", CompatStatus.COMPATIBLE)
    m.declare("app-1", "1.0.0", "3.0", CompatStatus.INCOMPATIBLE, "API removed")
    m.declare("app-1", "2.0.0", "3.0", CompatStatus.COMPATIBLE)
    m.declare("app-1", "2.0.0", "2.0", CompatStatus.COMPATIBLE)
    m.declare("app-2", "1.0.0", "2.0", CompatStatus.COMPATIBLE)
    m.declare("app-2", "1.0.0", "3.0", CompatStatus.DEGRADED, "Minor UI issues")
    return m


class TestDeclare:
    def test_declare_and_get(self):
        m = AppCompatibilityMatrix()
        entry = m.declare("app-1", "1.0.0", "2.0", CompatStatus.COMPATIBLE)
        assert entry.status == CompatStatus.COMPATIBLE
        assert m.get("app-1", "1.0.0", "2.0") is not None

    def test_get_nonexistent(self):
        m = AppCompatibilityMatrix()
        assert m.get("app-x", "1.0.0", "2.0") is None

    def test_get_status_untested(self):
        m = AppCompatibilityMatrix()
        assert m.get_status("app-x", "1.0.0", "9.0") == CompatStatus.UNTESTED

    def test_notes_stored(self):
        m = AppCompatibilityMatrix()
        entry = m.declare("app-1", "1.0.0", "3.0", CompatStatus.INCOMPATIBLE, "Breaking change")
        assert entry.notes == "Breaking change"


class TestImpactAnalysis:
    def test_safe_upgrade(self):
        m = _setup()
        report = m.analyze_upgrade_impact("2.0", [("app-1", "1.0.0"), ("app-2", "1.0.0")])
        assert report.safe_to_upgrade is True
        assert len(report.compatible) == 2
        assert len(report.incompatible) == 0

    def test_unsafe_with_incompatible(self):
        m = _setup()
        report = m.analyze_upgrade_impact("3.0", [("app-1", "1.0.0"), ("app-2", "1.0.0")])
        assert report.safe_to_upgrade is False
        assert len(report.incompatible) == 1
        assert report.incompatible[0].app_id == "app-1"

    def test_degraded_apps_reported(self):
        m = _setup()
        report = m.analyze_upgrade_impact("3.0", [("app-2", "1.0.0")])
        assert len(report.degraded) == 1
        assert report.degraded[0].notes == "Minor UI issues"

    def test_untested_apps(self):
        m = _setup()
        report = m.analyze_upgrade_impact("3.0", [("app-3", "1.0.0")])
        assert "app-3" in report.untested
        assert report.safe_to_upgrade is False  # untested = not safe

    def test_empty_installed(self):
        m = _setup()
        report = m.analyze_upgrade_impact("3.0", [])
        assert report.safe_to_upgrade is True
        assert len(report.compatible) == 0


class TestUpgradePath:
    def test_current_version_compatible(self):
        m = _setup()
        path = m.find_upgrade_path("app-1", "2.0.0", "3.0")
        assert path.recommended_version == "2.0.0"
        assert path.status == CompatStatus.COMPATIBLE

    def test_needs_upgrade(self):
        m = _setup()
        path = m.find_upgrade_path("app-1", "1.0.0", "3.0")
        assert path.recommended_version == "2.0.0"
        assert path.status == CompatStatus.COMPATIBLE

    def test_degraded_fallback(self):
        m = AppCompatibilityMatrix()
        m.declare("app-x", "1.0.0", "3.0", CompatStatus.INCOMPATIBLE)
        m.declare("app-x", "1.5.0", "3.0", CompatStatus.DEGRADED)
        path = m.find_upgrade_path("app-x", "1.0.0", "3.0")
        assert path.recommended_version == "1.5.0"
        assert path.status == CompatStatus.DEGRADED

    def test_no_compatible_version(self):
        m = AppCompatibilityMatrix()
        m.declare("app-x", "1.0.0", "3.0", CompatStatus.INCOMPATIBLE)
        path = m.find_upgrade_path("app-x", "1.0.0", "3.0")
        assert path.recommended_version is None
        assert path.status == CompatStatus.INCOMPATIBLE

    def test_unknown_app(self):
        m = _setup()
        path = m.find_upgrade_path("unknown", "1.0.0", "3.0")
        assert path.recommended_version is None


class TestMatrixQueries:
    def test_app_matrix(self):
        m = _setup()
        entries = m.get_app_matrix("app-1")
        assert len(entries) == 4
        assert all(e.app_id == "app-1" for e in entries)

    def test_platform_matrix(self):
        m = _setup()
        entries = m.get_platform_matrix("2.0")
        assert len(entries) == 3  # app-1 v1+v2, app-2 v1
        assert all(e.platform_version == "2.0" for e in entries)

    def test_empty_matrix(self):
        m = AppCompatibilityMatrix()
        assert m.get_app_matrix("app-x") == []
        assert m.get_platform_matrix("9.0") == []
