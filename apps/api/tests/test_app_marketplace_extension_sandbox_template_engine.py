from app.services.app_marketplace_extension_sandbox_template_engine import SandboxTemplateEngineService

def test_seed_templates():
    svc = SandboxTemplateEngineService()
    assert len(svc.list_all()) >= 2
    assert svc.get("python-basic") is not None

def test_instantiate():
    svc = SandboxTemplateEngineService()
    result = svc.instantiate("python-basic")
    assert result["runtime"] == "python"
    assert "main.py" in result["files"]

def test_instantiate_with_overrides():
    svc = SandboxTemplateEngineService()
    result = svc.instantiate("python-basic", {"main.py": "print('custom')"})
    assert result["files"]["main.py"] == "print('custom')"

def test_create_custom():
    svc = SandboxTemplateEngineService()
    svc.create("go-basic", "Go Basic", "go", {"main.go": "package main"})
    assert "go" in svc.get_runtimes()
