from app.services.app_marketplace_extension_perm_audit import PermAuditEngineService
import time


def test_unused_permission_detected():
    svc = PermAuditEngineService()
    svc.grant("ext-1", "read:profile")
    svc.grant("ext-1", "write:data")
    svc.record_use("ext-1", "read:profile")
    # write:data never used
    result = svc.audit("ext-1")
    assert result.total_permissions == 2
    assert result.used_permissions == 1
    assert any("write:data" in u for u in result.unused_permissions)


def test_dangerous_combo_detected():
    svc = PermAuditEngineService()
    svc.grant("ext-1", "sandbox:execute")
    svc.grant("ext-1", "webhook:manage")
    result = svc.audit("ext-1")
    assert len(result.dangerous_combos) == 1
    assert "exfiltration" in result.dangerous_combos[0]


def test_risk_score():
    svc = PermAuditEngineService()
    svc.grant("ext-1", "read:profile")  # risk 1
    svc.grant("ext-1", "admin:settings")  # risk 5
    result = svc.audit("ext-1")
    assert result.risk_score == 6


def test_version_escalation():
    svc = PermAuditEngineService()
    svc.record_version_permissions("ext-1", "1.0.0", {"read:profile"})
    svc.record_version_permissions("ext-1", "2.0.0", {"read:profile", "admin:settings"})
    # Grant current perms for audit
    svc.grant("ext-1", "read:profile")
    svc.grant("ext-1", "admin:settings")
    svc.record_use("ext-1", "read:profile")
    svc.record_use("ext-1", "admin:settings")
    result = svc.audit("ext-1")
    assert len(result.escalations) == 1
    assert "admin:settings" in result.escalations[0]


def test_clean_audit():
    svc = PermAuditEngineService()
    svc.grant("ext-1", "read:profile")
    svc.record_use("ext-1", "read:profile")
    result = svc.audit("ext-1")
    assert result.recommendation.startswith("✅")
    assert len(result.unused_permissions) == 0


def test_stale_permission():
    svc = PermAuditEngineService()
    svc.grant("ext-1", "read:data")
    usage = svc._usage["ext-1"]["read:data"]
    usage.use_count = 5
    usage.last_used = time.time() - 60 * 86400  # 60 days ago
    result = svc.audit("ext-1", stale_days=30)
    assert any("stale" in u for u in result.unused_permissions)
