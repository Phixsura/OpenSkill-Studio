from app.services.app_marketplace_complete_sandbox_page_v2 import build_complete_sandbox_page_v2

def test_running():
    p = build_complete_sandbox_page_v2(
        app={"id": "a1", "name": "App"}, sandbox={"status": "running", "uptime": 45},
        console_history=[{"cmd": "ls"}], filesystem={"file_count": 10},
        resources={"cpu": 30, "memory": 128}, network={"requests": 50},
        snapshots=[{"name": "v1"}])
    assert p["sandbox"]["status"] == "running"
    assert p["actions"]["stop"]
    assert not p["actions"]["start"]
    assert len(p["panels"]) == 6
