from app.services.app_marketplace_app_app_app_app_app_app_app_release_gate import create_gate, evaluate_gate

def test_pass():
    g = create_gate("v2.0", [
        {"name": "tests", "type": "required"},
        {"name": "lint", "type": "required"},
        {"name": "coverage", "type": "optional"},
    ])
    r = evaluate_gate(g, {"tests": True, "lint": True, "coverage": True})
    assert r["can_release"]
    assert r["passed"] == 3

def test_block():
    g = create_gate("v3.0", [
        {"name": "tests", "type": "required"},
        {"name": "security", "type": "required"},
    ])
    r = evaluate_gate(g, {"tests": True, "security": False})
    assert not r["can_release"]
    assert r["blocking"]
