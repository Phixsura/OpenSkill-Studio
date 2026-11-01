from app.services.app_marketplace_extension_sandbox_config_template import (
    SandboxConfigTemplateService,
)


def test_register_and_render():
    svc = SandboxConfigTemplateService()
    svc.register("db", "Database Config", {
        "host": "{{db_host}}:{{db_port}}",
        "name": "{{db_name}}",
    }, [
        {"name": "db_host"}, {"name": "db_port", "default": "5432"},
        {"name": "db_name"},
    ])
    result = svc.render("db", {"db_host": "localhost", "db_name": "myapp"})
    assert result["host"] == "localhost:5432"
    assert result["name"] == "myapp"


def test_missing_required():
    svc = SandboxConfigTemplateService()
    svc.register("t", "T", {"k": "{{val}}"}, [{"name": "val"}])
    result = svc.render("t", {})
    assert "error" in result


def test_enum_validation():
    svc = SandboxConfigTemplateService()
    svc.register("t", "T", {"env": "{{env}}"},
                 [{"name": "env", "enum": ["dev", "prod"]}])
    result = svc.render("t", {"env": "staging"})
    assert "error" in result


def test_defaults():
    svc = SandboxConfigTemplateService()
    svc.register("t", "T", {"port": "{{port}}"},
                 [{"name": "port", "default": "3000", "required": False}])
    result = svc.render("t", {})
    assert result["port"] == "3000"


def test_list_templates():
    svc = SandboxConfigTemplateService()
    svc.register("a", "A", {}, [])
    svc.register("b", "B", {}, [{"name": "x"}])
    listed = svc.list_templates()
    assert len(listed) == 2
