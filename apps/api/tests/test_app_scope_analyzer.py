"""Tests for App Scope Analyzer — usage tracking, compliance, recommendations."""

import pytest

from app.services.app_scope_analyzer import AppScopeAnalyzer


class TestDeclareAndRecord:
    def test_declare_scopes(self):
        a = AppScopeAnalyzer()
        a.declare_scopes("app-1", ["read:skills", "write:projects"])
        analysis = a.analyze("app-1")
        assert analysis.declared_scopes == {"read:skills", "write:projects"}

    def test_record_declared_scope(self):
        a = AppScopeAnalyzer()
        a.declare_scopes("app-1", ["read:skills"])
        assert a.record_usage("app-1", "read:skills", "/api/v1/skills") is True

    def test_record_undeclared_scope(self):
        a = AppScopeAnalyzer()
        a.declare_scopes("app-1", ["read:skills"])
        assert a.record_usage("app-1", "admin:org", "/api/v1/admin") is False

    def test_denied_tracked(self):
        a = AppScopeAnalyzer()
        a.declare_scopes("app-1", [])
        a.record_usage("app-1", "admin:org", "/api/v1/admin")
        assert "admin:org" in a.get_denied_attempts("app-1")


class TestAnalysis:
    def test_all_used(self):
        a = AppScopeAnalyzer()
        a.declare_scopes("app-1", ["read:skills", "write:projects"])
        a.record_usage("app-1", "read:skills", "/skills")
        a.record_usage("app-1", "write:projects", "/projects")
        result = a.analyze("app-1")
        assert result.compliance_pct == 100.0
        assert result.over_permissioned is False
        assert result.under_permissioned is False
        assert len(result.unused_scopes) == 0

    def test_over_permissioned(self):
        a = AppScopeAnalyzer()
        a.declare_scopes("app-1", ["read:skills", "write:projects", "read:email"])
        a.record_usage("app-1", "read:skills", "/skills")
        result = a.analyze("app-1")
        assert result.over_permissioned is True
        assert "write:projects" in result.unused_scopes
        assert "read:email" in result.unused_scopes
        assert result.compliance_pct == pytest.approx(33.3, abs=0.1)

    def test_under_permissioned(self):
        a = AppScopeAnalyzer()
        a.declare_scopes("app-1", ["read:skills"])
        a.record_usage("app-1", "read:skills", "/skills")
        a.record_usage("app-1", "admin:org", "/admin")
        result = a.analyze("app-1")
        assert result.under_permissioned is True
        assert "admin:org" in result.undeclared_attempts

    def test_both_over_and_under(self):
        a = AppScopeAnalyzer()
        a.declare_scopes("app-1", ["read:skills", "read:email"])
        a.record_usage("app-1", "read:skills", "/skills")
        a.record_usage("app-1", "admin:org", "/admin")
        result = a.analyze("app-1")
        assert result.over_permissioned is True
        assert result.under_permissioned is True

    def test_no_declarations(self):
        a = AppScopeAnalyzer()
        result = a.analyze("app-x")
        assert result.compliance_pct == 100.0
        assert result.declared_scopes == set()

    def test_no_usage(self):
        a = AppScopeAnalyzer()
        a.declare_scopes("app-1", ["read:skills"])
        result = a.analyze("app-1")
        assert result.compliance_pct == 0.0
        assert result.over_permissioned is True


class TestRecommendations:
    def test_remove_unused(self):
        a = AppScopeAnalyzer()
        a.declare_scopes("app-1", ["read:skills", "write:projects"])
        a.record_usage("app-1", "read:skills", "/skills")
        result = a.analyze("app-1")
        assert any("Remove" in r for r in result.recommendations)
        assert any("write:projects" in r for r in result.recommendations)

    def test_add_missing(self):
        a = AppScopeAnalyzer()
        a.declare_scopes("app-1", [])
        a.record_usage("app-1", "admin:org", "/admin")
        result = a.analyze("app-1")
        assert any("Add" in r for r in result.recommendations)

    def test_perfect_no_changes(self):
        a = AppScopeAnalyzer()
        a.declare_scopes("app-1", ["read:skills"])
        a.record_usage("app-1", "read:skills", "/skills")
        result = a.analyze("app-1")
        assert any("no changes" in r.lower() for r in result.recommendations)


class TestTopScopes:
    def test_ranking(self):
        a = AppScopeAnalyzer()
        a.declare_scopes("app-1", ["read:skills", "write:projects"])
        for _ in range(10):
            a.record_usage("app-1", "read:skills", "/skills")
        for _ in range(3):
            a.record_usage("app-1", "write:projects", "/projects")
        top = a.get_top_scopes("app-1")
        assert top[0] == ("read:skills", 10)
        assert top[1] == ("write:projects", 3)

    def test_empty(self):
        a = AppScopeAnalyzer()
        assert a.get_top_scopes("app-x") == []

    def test_limit(self):
        a = AppScopeAnalyzer()
        a.declare_scopes("app-1", [f"scope:{i}" for i in range(20)])
        for i in range(20):
            a.record_usage("app-1", f"scope:{i}", "/ep")
        assert len(a.get_top_scopes("app-1", limit=5)) == 5
