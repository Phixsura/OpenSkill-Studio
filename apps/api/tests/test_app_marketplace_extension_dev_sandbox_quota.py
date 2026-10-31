from app.services.app_marketplace_extension_dev_sandbox_quota import DevSandboxQuotaService

def test_free_tier():
    svc = DevSandboxQuotaService()
    q = svc.get_or_create("dev1", "free")
    assert q.max_sandboxes == 3

def test_allocate_and_release():
    svc = DevSandboxQuotaService()
    svc.get_or_create("dev1", "free")
    assert svc.allocate("dev1", 64) is True
    assert svc._quotas["dev1"].active_sandboxes == 1
    svc.release("dev1", 64)
    assert svc._quotas["dev1"].active_sandboxes == 0

def test_limit_reached():
    svc = DevSandboxQuotaService()
    svc.get_or_create("dev1", "free")
    for _ in range(3):
        svc.allocate("dev1", 64)
    ok, msg = svc.can_create_sandbox("dev1")
    assert ok is False

def test_upgrade():
    svc = DevSandboxQuotaService()
    svc.get_or_create("dev1", "free")
    svc.upgrade_tier("dev1", "pro")
    assert svc._quotas["dev1"].max_sandboxes == 10
