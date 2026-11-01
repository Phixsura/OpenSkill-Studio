"""Tests for Consumer API Key Scope Audit service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_scope_audit import ScopeAudit


class TestScopeAudit:
    def test_register_and_audit(self):
        svc = ScopeAudit()
        svc.register_key("k1", "c1", ["read", "write", "admin"])
        svc.record_usage("k1", "read")
        audit = svc.audit_key("k1")
        assert "write" in audit["unused_scopes"]
        assert "admin" in audit["unused_scopes"]

    def test_optimal_key(self):
        svc = ScopeAudit()
        svc.register_key("k1", "c1", ["read", "write"])
        svc.record_usage("k1", "read")
        svc.record_usage("k1", "write")
        audit = svc.audit_key("k1")
        assert audit["recommendation"] == "optimal"
        assert audit["over_permission_pct"] == 0

    def test_over_permissioned(self):
        svc = ScopeAudit()
        svc.register_key("k1", "c1", ["read", "write", "admin", "delete"])
        svc.record_usage("k1", "read")
        audit = svc.audit_key("k1")
        assert audit["over_permission_pct"] == 75.0
        assert audit["recommendation"] == "reduce_scopes"

    def test_used_outside_grant(self):
        svc = ScopeAudit()
        svc.register_key("k1", "c1", ["read"])
        svc.record_usage("k1", "read")
        svc.record_usage("k1", "write")
        audit = svc.audit_key("k1")
        assert "write" in audit["used_outside_grant"]
        assert audit["recommendation"] == "expand_grant"

    def test_get_over_permissioned(self):
        svc = ScopeAudit()
        svc.register_key("k1", "c1", ["a", "b", "c", "d"])
        svc.record_usage("k1", "a")
        svc.register_key("k2", "c1", ["x"])
        svc.record_usage("k2", "x")
        over = svc.get_over_permissioned(50.0)
        assert len(over) == 1
        assert over[0]["key_id"] == "k1"

    def test_audit_all_sorted(self):
        svc = ScopeAudit()
        svc.register_key("k1", "c1", ["a", "b"])
        svc.record_usage("k1", "a")
        svc.record_usage("k1", "b")
        svc.register_key("k2", "c1", ["x", "y", "z"])
        svc.record_usage("k2", "x")
        audits = svc.audit_all()
        assert audits[0]["key_id"] == "k2"  # higher over-perm

    def test_stats(self):
        svc = ScopeAudit()
        svc.register_key("k1", "c1", ["a", "b"])
        svc.record_usage("k1", "a")
        svc.record_usage("k1", "b")
        stats = svc.get_stats()
        assert stats["total_keys"] == 1
        assert stats["optimal"] == 1

    def test_not_found(self):
        svc = ScopeAudit()
        assert svc.audit_key("missing")["error"] == "not_found"

    def test_duplicate_key(self):
        svc = ScopeAudit()
        svc.register_key("k1", "c1", ["a"])
        with pytest.raises(ValueError):
            svc.register_key("k1", "c2", ["b"])

    def test_unknown_key_usage(self):
        svc = ScopeAudit()
        with pytest.raises(ValueError):
            svc.record_usage("missing", "read")

    def test_isolation(self):
        a, b = ScopeAudit(), ScopeAudit()
        a.register_key("k1", "c1", ["read"])
        assert b.audit_key("k1")["error"] == "not_found"
