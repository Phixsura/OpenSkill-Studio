from app.services.app_marketplace_extension_audit_trail import ExtAuditTrailService

def test_record():
    svc = ExtAuditTrailService()
    e = svc.record("ext-1", "dev-1", "created", "Initial version")
    assert e.action == "created"

def test_invalid_action():
    svc = ExtAuditTrailService()
    try:
        svc.record("ext-1", "dev-1", "hacked")
        assert False
    except ValueError:
        pass

def test_by_extension():
    svc = ExtAuditTrailService()
    svc.record("ext-1", "dev-1", "created")
    svc.record("ext-1", "dev-1", "published")
    svc.record("ext-2", "dev-2", "created")
    assert len(svc.get_by_extension("ext-1")) == 2

def test_count_actions():
    svc = ExtAuditTrailService()
    svc.record("ext-1", "u1", "installed")
    svc.record("ext-1", "u2", "installed")
    svc.record("ext-1", "u1", "reviewed")
    counts = svc.count_actions("ext-1")
    assert counts["installed"] == 2
    assert counts["reviewed"] == 1
