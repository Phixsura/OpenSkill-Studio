from app.services.app_marketplace_install_guard import check_install_prerequisites

def test_can_install():
    r = check_install_prerequisites(app={"id": "a1"}, org={"app_limit": 10},
                                      existing_installs=[])
    assert r["can_install"]

def test_already_installed():
    r = check_install_prerequisites(app={"id": "a1"}, org={},
                                      existing_installs=[{"app_id": "a1", "status": "active"}])
    assert not r["can_install"]
    assert r["blockers"][0]["type"] == "already_installed"

def test_conflict():
    r = check_install_prerequisites(app={"id": "a1", "conflicts_with": ["a2"]}, org={},
                                      existing_installs=[{"app_id": "a2", "status": "active"}])
    assert not r["can_install"]
    assert r["blockers"][0]["type"] == "conflict"

def test_missing_dep():
    r = check_install_prerequisites(app={"id": "a1", "depends_on": ["auth"]}, org={},
                                      existing_installs=[])
    assert not r["can_install"]

def test_plan_limit():
    r = check_install_prerequisites(app={"id": "a3"}, org={"app_limit": 2},
                                      existing_installs=[{"app_id": "a1", "status": "active"}, {"app_id": "a2", "status": "active"}])
    assert not r["can_install"]

def test_admin_warning():
    r = check_install_prerequisites(app={"id": "a1", "requires_admin": True}, org={}, existing_installs=[])
    assert r["can_install"]
    assert len(r["warnings"]) == 1
