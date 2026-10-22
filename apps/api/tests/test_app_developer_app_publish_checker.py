from app.services.app_developer_app_publish_checker import check_publish_requirements

def test_can_publish():
    r = check_publish_requirements(app={"status": "approved", "description": "X", "visibility": "public", "privacy_policy_url": "u"},
        latest_version={"review_status": "approved"}, developer={"verified": True})
    assert r["can_publish"] is True

def test_not_approved():
    r = check_publish_requirements(app={"status": "draft"}, latest_version=None, developer={})
    assert r["can_publish"] is False

def test_warnings():
    r = check_publish_requirements(app={"status": "approved", "description": "X", "visibility": "private"},
        latest_version={"review_status": "approved"}, developer={"verified": False})
    assert r["can_publish"] is True
    assert len(r["warnings"]) >= 2
