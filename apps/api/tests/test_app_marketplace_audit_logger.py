from app.services.app_marketplace_audit_logger import AuditLogger, AuditAction


def test_log_and_query():
    al = AuditLogger()
    entry = al.log(AuditAction.EXTENSION_PUBLISHED, "dev-1", "user",
                    "extension", "ext-1", details={"version": "1.0.0"})
    assert entry.entry_id == "audit-1"
    assert entry.action == AuditAction.EXTENSION_PUBLISHED
    results = al.query(actor_id="dev-1")
    assert len(results) == 1


def test_filter_by_action():
    al = AuditLogger()
    al.log(AuditAction.EXTENSION_INSTALLED, "u1", "user", "extension", "e1")
    al.log(AuditAction.KEY_ISSUED, "u1", "user", "key", "k1")
    al.log(AuditAction.EXTENSION_INSTALLED, "u2", "user", "extension", "e2")
    installs = al.query(action=AuditAction.EXTENSION_INSTALLED)
    assert len(installs) == 2


def test_target_history():
    al = AuditLogger()
    al.log(AuditAction.EXTENSION_PUBLISHED, "dev", "user", "extension", "ext-5")
    al.log(AuditAction.EXTENSION_INSTALLED, "org", "user", "extension", "ext-5")
    al.log(AuditAction.CONFIG_CHANGED, "admin", "user", "extension", "ext-5")
    history = al.get_target_history("ext-5")
    assert len(history) == 3


def test_count():
    al = AuditLogger()
    al.log(AuditAction.REVIEW_SUBMITTED, "u1", "user", "extension", "e1")
    al.log(AuditAction.REVIEW_SUBMITTED, "u2", "user", "extension", "e1")
    assert al.count() == 2
    assert al.count(AuditAction.REVIEW_SUBMITTED) == 2
    assert al.count(AuditAction.KEY_REVOKED) == 0


def test_export():
    al = AuditLogger()
    al.log(AuditAction.BILLING_SUBSCRIBED, "org-1", "user", "plan", "p1")
    exported = al.export()
    assert len(exported) == 1
    assert exported[0]["action"] == "billing.subscribed"
    assert "entry_id" in exported[0]
