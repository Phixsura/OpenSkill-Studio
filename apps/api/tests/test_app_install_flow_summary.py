from app.services.app_install_flow_summary import build_install_flow

def test_with_config():
    f = build_install_flow(app={"name": "X"}, permissions=["read:cohorts"], org={"name": "Org"}, has_config=True)
    assert f["step_count"] == 3
    assert "configure" in f["steps"]

def test_without_config():
    f = build_install_flow(app={"name": "X"}, permissions=[], org={"name": "O"}, has_config=False)
    assert f["step_count"] == 2
    assert "configure" not in f["steps"]
