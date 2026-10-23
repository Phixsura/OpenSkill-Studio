from app.services.app_marketplace_install_success import build_install_success

def test_success():
    r = build_install_success(app={"name": "MyApp", "slug": "my-app"}, installation_id="inst_1",
                                scopes_granted=["read", "write"])
    assert r["success"]
    assert "MyApp" in r["message"]
    assert len(r["next_steps"]) == 3
    assert r["scopes_granted"] == ["read", "write"]
