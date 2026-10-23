from app.services.app_marketplace_content_policy import check_content_policy

def test_clean():
    r = check_content_policy(app_name="My Cool App",
        description="A fantastic productivity tool that helps teams collaborate effectively",
        category="productivity", screenshots=3)
    assert r["passed"]
    assert r["critical_count"] == 0

def test_forbidden_cat():
    r = check_content_policy(app_name="App", description="x" * 60, category="malware", screenshots=1)
    assert not r["passed"]
    assert r["critical_count"] == 1

def test_impersonation():
    r = check_content_policy(app_name="Official Google Maps", description="x" * 60,
        category="maps", screenshots=1)
    assert not r["passed"]

def test_warnings():
    r = check_content_policy(app_name="App", description="Short", category="tools", screenshots=0)
    assert r["passed"]  # warnings don't block
    assert r["warning_count"] == 2
