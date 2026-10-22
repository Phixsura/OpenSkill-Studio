from app.services.app_marketplace_complete_sandbox_page import build_complete_sandbox_page

def test_page():
    p = build_complete_sandbox_page(
        app={"id": "a1", "name": "App"}, sandbox_status={"running": True},
        filesystem={"files": 5, "used_bytes": 1024}, console_history=[{"input": "hi"}],
        resource_usage={"cpu_pct": 30}, network_policy={"allowed_hosts": ["api.com"]},
        logs=[{"level": "info", "message": "Started"}])
    assert p["page_type"] == "sandbox_environment"
    assert len(p["panels"]) == 5
    assert "Files (5)" in p["panels"][1]["title"]

def test_empty():
    p = build_complete_sandbox_page(
        app={"id": "a1", "name": "X"}, sandbox_status={}, filesystem={"files": 0},
        console_history=[], resource_usage={}, network_policy={}, logs=[])
    assert p["panels"][4]["title"] == "Logs (0)"
