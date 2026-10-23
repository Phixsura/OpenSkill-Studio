from app.services.app_marketplace_app_cli_generator import generate_cli_config

def test_generate():
    commands = [
        {"name": "init", "description": "Initialize project",
         "args": [{"name": "template", "type": "string", "required": True}]},
        {"name": "deploy", "description": "Deploy app"},
    ]
    r = generate_cli_config(app_name="My Cool App", commands=commands)
    assert r["cli_name"] == "my-cool-app"
    assert r["total_commands"] == 2
    assert r["commands"][0]["args"][0]["name"] == "template"
    assert "npm install" in r["install_cmd"]

def test_invalid_name():
    r = generate_cli_config(app_name="!!!", commands=[])
    assert "error" in r
