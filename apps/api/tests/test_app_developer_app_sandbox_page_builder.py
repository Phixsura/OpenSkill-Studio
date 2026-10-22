from app.services.app_developer_app_sandbox_page_builder import build_sandbox_page

def test_page():
    p = build_sandbox_page(sandbox_config={"runtime": "python3.12"}, recent_executions=[{"id": "e1"}], total_executions=50)
    assert p["configured"] is True
    assert p["total_executions"] == 50
