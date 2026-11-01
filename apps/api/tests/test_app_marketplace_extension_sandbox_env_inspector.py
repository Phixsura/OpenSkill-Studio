from app.services.app_marketplace_extension_sandbox_env_inspector import (
    SandboxEnvInspectorService,
)


def test_inspect():
    svc = SandboxEnvInspectorService()
    result = svc.inspect("sb-1", "node", "20.10.0",
                         packages=[{"name": "express", "version": "4.18.0", "size_kb": 500}],
                         available_apis=["fetch", "crypto"],
                         limits=[{"name": "memory", "current": 200, "max": 256, "unit": "MB"}],
                         env_vars_count=5)
    assert result.runtime == "node"
    assert len(result.packages) == 1
    assert len(result.available_apis) == 2


def test_diagnostics_high_usage():
    svc = SandboxEnvInspectorService()
    result = svc.inspect("sb-1", "node", "20",
                         limits=[{"name": "CPU", "current": 90, "max": 100}])
    assert any("CPU" in d for d in result.diagnostics)


def test_diagnostics_no_apis():
    svc = SandboxEnvInspectorService()
    result = svc.inspect("sb-1", "node", "20", available_apis=[])
    assert any("No APIs" in d for d in result.diagnostics)


def test_search_packages():
    svc = SandboxEnvInspectorService()
    svc.inspect("sb-1", "node", "20", packages=[
        {"name": "express", "version": "4.18"}, {"name": "lodash", "version": "4.17"},
        {"name": "express-validator", "version": "7.0"},
    ])
    results = svc.search_packages("sb-1", "express")
    assert len(results) == 2


def test_check_api():
    svc = SandboxEnvInspectorService()
    svc.inspect("sb-1", "node", "20", available_apis=["fetch", "crypto"])
    assert svc.check_api_available("sb-1", "fetch") is True
    assert svc.check_api_available("sb-1", "fs") is False


def test_summary():
    svc = SandboxEnvInspectorService()
    svc.inspect("sb-1", "python", "3.12",
                packages=[{"name": "requests", "version": "2.31"}],
                available_apis=["json", "math"],
                env_vars_count=10)
    summary = svc.get_summary("sb-1")
    assert summary["runtime"] == "python 3.12"
    assert summary["packages"] == 1
    assert summary["apis"] == 2
