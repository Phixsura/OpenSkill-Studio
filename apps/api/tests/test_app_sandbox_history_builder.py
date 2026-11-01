from app.services.app_sandbox_history_builder import build_sandbox_history_page

def test_page():
    p = build_sandbox_history_page(executions=[{"id": "e1"}], total=100, page=1, per_page=20, success_rate=98.5, avg_duration_ms=150)
    assert p["total_pages"] == 5
    assert p["summary"]["success_rate"] == 98.5
