from app.services.app_developer_app_version_manager import compute_version_status, can_create_new_version

VERSIONS = [{"version": "2.0", "review_status": "approved"}, {"version": "1.0", "review_status": "approved"}]

def test_status():
    s = compute_version_status(VERSIONS)
    assert s["total"] == 2
    assert s["approved"] == 2
    assert s["latest_version"] == "2.0"

def test_can_create():
    r = can_create_new_version(VERSIONS)
    assert r["allowed"] is True

def test_cannot_create_pending():
    r = can_create_new_version([{"version": "1.0", "review_status": "pending"}])
    assert r["allowed"] is False

def test_empty():
    s = compute_version_status([])
    assert s["latest_version"] is None
