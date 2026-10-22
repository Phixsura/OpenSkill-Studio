from app.services.app_cli_commands import generate_init_commands, generate_deploy_commands

def test_init_python():
    cmds = generate_init_commands(app_name="My App", slug="my-app", category="connector", runtime="python3.12")
    assert any("pip install" in c for c in cmds)
    assert any("my-app" in c for c in cmds)

def test_init_node():
    cmds = generate_init_commands(app_name="X", slug="x", category="automation", runtime="nodejs20")
    assert any("npm install" in c for c in cmds)

def test_deploy():
    cmds = generate_deploy_commands("my-app")
    assert any("deploy" in c for c in cmds)
    assert any("logs" in c for c in cmds)
