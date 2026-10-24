from app.services.app_marketplace_app_app_app_app_app_app_app_cli_builder import build_cli_command, generate_cli_examples

def test_build():
    r = build_cli_command(command="openskill deploy", args={"app": "myapp"},
                           flags={"env": "production", "wait": True})
    assert "openskill deploy" in r["command"]
    assert "--env=production" in r["command"]
    assert "--wait" in r["command"]

def test_examples():
    examples = generate_cli_examples("myapp")
    assert len(examples) == 4
    assert "deploy" in examples[0]["command"]
    assert "logs" in examples[1]["command"]
