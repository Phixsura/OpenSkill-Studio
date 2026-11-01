from app.services.app_marketplace_extension_bundle_mgr import ExtBundleMgrService

def test_create_bundle():
    svc = ExtBundleMgrService()
    b = svc.create("Starter Pack", "Essential extensions", ["ext-1", "ext-2", "ext-3"], "dev-1", 20)
    assert len(b.extensions) == 3
    assert b.discount_pct == 20

def test_min_extensions():
    svc = ExtBundleMgrService()
    try:
        svc.create("Solo", "One ext", ["ext-1"], "dev-1")
        assert False
    except ValueError:
        pass

def test_install():
    svc = ExtBundleMgrService()
    b = svc.create("Pack", "desc", ["ext-1", "ext-2"], "dev-1")
    exts = svc.install(b.bundle_id)
    assert exts == ["ext-1", "ext-2"]
    assert b.install_count == 1

def test_get_containing():
    svc = ExtBundleMgrService()
    svc.create("A", "a", ["ext-1", "ext-2"], "dev-1")
    svc.create("B", "b", ["ext-2", "ext-3"], "dev-1")
    assert len(svc.get_containing("ext-2")) == 2
