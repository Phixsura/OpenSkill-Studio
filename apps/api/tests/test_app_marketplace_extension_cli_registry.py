from app.services.app_marketplace_extension_cli_registry import ExtCliRegistryService

def test_register_and_add_command():
    svc = ExtCliRegistryService()
    tool = svc.register("ext-1", "myext", "1.0.0", "npm i -g myext")
    svc.add_command(tool.tool_id, "init", "Initialize project", "myext init [dir]")
    svc.add_command(tool.tool_id, "build", "Build project", "myext build")
    assert len(tool.commands) == 2

def test_search():
    svc = ExtCliRegistryService()
    svc.register("ext-1", "deploy-tool", "1.0")
    svc.register("ext-2", "lint-checker", "1.0")
    results = svc.search("deploy")
    assert len(results) == 1

def test_help():
    svc = ExtCliRegistryService()
    tool = svc.register("ext-1", "mycli", "2.0", "pip install mycli")
    svc.add_command(tool.tool_id, "run", "Run task", "mycli run [task]")
    help_text = svc.generate_help(tool.tool_id)
    assert "mycli v2.0" in help_text
    assert "mycli run [task]" in help_text
