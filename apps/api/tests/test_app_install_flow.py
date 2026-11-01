from app.services.app_install_flow import validate_full_install_flow

def test_allowed():
    r = validate_full_install_flow(
        app={"status": "published", "category": "connector", "manifest": {"permissions": ["read:cohorts"]}},
        version={"review_status": "approved"},
        org={"app_count": 5, "max_apps": 50},
        already_installed=False,
    )
    assert r["allowed"] is True

def test_not_published():
    r = validate_full_install_flow(
        app={"status": "draft", "category": "connector"},
        version={"review_status": "approved"},
        org={"app_count": 0},
        already_installed=False,
    )
    assert r["allowed"] is False

def test_already_installed():
    r = validate_full_install_flow(
        app={"status": "published"},
        version={"review_status": "approved"},
        org={"app_count": 0},
        already_installed=True,
    )
    assert r["allowed"] is False
