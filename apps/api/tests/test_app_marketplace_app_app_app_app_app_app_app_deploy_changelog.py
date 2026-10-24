from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_changelog import generate_deploy_changelog

def test_changelog():
    r = generate_deploy_changelog("3.1.0", [
        {"type": "feat", "message": "Add dark mode"},
        {"type": "feat", "message": "OAuth support"},
        {"type": "fix", "message": "Login bug"},
    ], "alice")
    assert r["commit_count"] == 3
    assert r["type_count"] == 2
    assert any(s["label"] == "Features" for s in r["sections"])
