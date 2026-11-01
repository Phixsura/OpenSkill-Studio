from app.services.app_marketplace_app_cli_tool_generator import generate_install_command, generate_config_command, generate_cli_reference

def test_install():
    cmd = generate_install_command(app_slug="my-app", org_id="org1")
    assert "openskill apps install my-app" in cmd
    assert "--org org1" in cmd

def test_config():
    cmd = generate_config_command(app_slug="my-app", key="timeout", value="30")
    assert "config set my-app timeout=30" in cmd

def test_reference():
    r = generate_cli_reference(app={"name": "MyApp", "slug": "my-app"})
    assert r["app_name"] == "MyApp"
    assert len(r["commands"]) == 6
    assert any("install" in c["command"] for c in r["commands"])
