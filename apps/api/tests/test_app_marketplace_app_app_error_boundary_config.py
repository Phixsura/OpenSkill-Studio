from app.services.app_marketplace_app_app_error_boundary_config import build_error_boundary_config

def test_config():
    r = build_error_boundary_config(app_name="Auth SDK", show_details=True)
    assert r["fallback"]["title"] == "Something went wrong"
    assert "Auth SDK" in r["fallback"]["message"]
    assert r["show_stack_trace"]
    assert r["retry_count"] == 3
    assert len(r["fallback"]["actions"]) == 2

def test_production():
    r = build_error_boundary_config(app_name="App", show_details=False)
    assert not r["show_stack_trace"]
    assert r["report_to_service"]
