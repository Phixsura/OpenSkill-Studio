from app.services.app_marketplace_install_flow import (
    validate_install_prerequisites, create_installation_record, build_install_confirmation,
)

def test_valid_install():
    r = validate_install_prerequisites(
        app={"status": "published", "current_version_id": "v1", "required_scopes": ["read"]},
        org={"id": "org1", "granted_scopes": ["read", "write"]}, user={"id": "u1"})
    assert r["valid"]

def test_unpublished_rejected():
    r = validate_install_prerequisites(
        app={"status": "draft", "current_version_id": "v1"},
        org={"id": "org1", "granted_scopes": []}, user={"id": "u1"})
    assert not r["valid"]
    assert "not published" in r["errors"][0]

def test_missing_scopes():
    r = validate_install_prerequisites(
        app={"status": "published", "current_version_id": "v1", "required_scopes": ["admin"]},
        org={"id": "org1", "granted_scopes": ["read"]}, user={"id": "u1"})
    assert not r["valid"]
    assert "admin" in r["errors"][0]

def test_create_record():
    rec = create_installation_record(app={"id": "a1", "name": "X", "default_config": {"k": "v"}},
                                      org_id="org1", user_id="u1", version_id="v1")
    assert rec["status"] == "active"
    assert rec["config"] == {"k": "v"}

def test_confirmation():
    c = build_install_confirmation(app={"name": "MyApp"}, installation={"id": "inst_1"})
    assert "MyApp" in c["message"]
    assert len(c["next_steps"]) == 3
