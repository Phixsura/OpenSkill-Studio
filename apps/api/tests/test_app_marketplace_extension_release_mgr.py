from app.services.app_marketplace_extension_release_mgr import ExtReleaseMgrService

def test_full_lifecycle():
    svc = ExtReleaseMgrService()
    r = svc.create_draft("ext-1", "2.0.0", ["New feature", "Bug fix"])
    assert svc.submit_for_review(r.release_id) is True
    assert svc.approve(r.release_id, "reviewer-1") is True
    assert svc.publish(r.release_id) is True
    assert r.status == "published"

def test_reject():
    svc = ExtReleaseMgrService()
    r = svc.create_draft("ext-1", "1.0.0", ["Initial"])
    svc.submit_for_review(r.release_id)
    svc.reject(r.release_id, "rev-1", "Needs fixes")
    assert r.status == "rejected"

def test_no_publish_without_approval():
    svc = ExtReleaseMgrService()
    r = svc.create_draft("ext-1", "1.0.0", ["Change"])
    svc.submit_for_review(r.release_id)
    assert svc.publish(r.release_id) is False

def test_no_submit_empty_changelog():
    svc = ExtReleaseMgrService()
    r = svc.create_draft("ext-1", "1.0.0", [])
    assert svc.submit_for_review(r.release_id) is False
