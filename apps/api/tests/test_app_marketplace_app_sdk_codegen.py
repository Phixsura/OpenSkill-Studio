from app.services.app_marketplace_app_sdk_codegen import generate_typescript_client, generate_python_client, list_supported_languages

def test_typescript():
    code = generate_typescript_client(app={"name": "MyApp", "version": "2.0"},
                                       endpoints=[{"path": "/users", "method": "GET", "operation_id": "getUsers"}])
    assert "class AppClient" in code
    assert "getUsers" in code
    assert "Bearer" in code

def test_python():
    code = generate_python_client(app={"name": "MyApp"},
                                    endpoints=[{"path": "/apps", "method": "GET", "operation_id": "list_apps"}])
    assert "class AppClient" in code
    assert "list_apps" in code
    assert "httpx" in code

def test_languages():
    langs = list_supported_languages()
    assert "typescript" in langs
    assert "python" in langs
    assert len(langs) >= 5
