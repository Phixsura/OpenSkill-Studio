from app.services.app_marketplace_app_app_quickstart_guide import generate_quickstart

def test_typescript():
    r = generate_quickstart(app_name="Auth SDK", sdk="typescript")
    assert r["total_steps"] == 4
    assert "npm install" in r["steps"][0]["code"]
    assert r["estimated_time_min"] == 5

def test_python():
    r = generate_quickstart(app_name="Auth SDK", sdk="python")
    assert "pip install" in r["steps"][0]["code"]
    assert "Client" in r["steps"][1]["code"]
