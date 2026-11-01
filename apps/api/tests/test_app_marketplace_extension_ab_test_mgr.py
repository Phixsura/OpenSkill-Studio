from app.services.app_marketplace_extension_ab_test_mgr import ExtABTestMgrService

def test_create_and_assign():
    svc = ExtABTestMgrService()
    test = svc.create("ext-1", "title", [("a", "Original", 0.5), ("b", "New Title", 0.5)])
    vid = svc.assign(test.test_id, "user-1")
    assert vid in ("a", "b")

def test_deterministic():
    svc = ExtABTestMgrService()
    test = svc.create("ext-1", "title", [("a", "A", 0.5), ("b", "B", 0.5)])
    v1 = svc.assign(test.test_id, "user-1")
    v2 = svc.assign(test.test_id, "user-1")
    # Same user same test = same variant (but impressions counted twice)
    assert v1 == v2

def test_conversion():
    svc = ExtABTestMgrService()
    test = svc.create("ext-1", "title", [("a", "A", 0.5), ("b", "B", 0.5)])
    svc.record_conversion(test.test_id, "a")
    results = svc.get_results(test.test_id)
    assert results["variants"][0]["conversions"] == 1

def test_invalid_weights():
    svc = ExtABTestMgrService()
    try:
        svc.create("ext-1", "title", [("a", "A", 0.3), ("b", "B", 0.3)])
        assert False
    except ValueError:
        pass
