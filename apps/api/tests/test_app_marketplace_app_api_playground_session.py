from app.services.app_marketplace_app_api_playground_session import create_session, add_variable, interpolate_variables, add_to_history

def test_create():
    s = create_session(developer_id="d1", app_id="a1", base_url="https://api.example.com")
    assert s["status"] == "active"

def test_add_var():
    s = create_session(developer_id="d1", app_id="a1", base_url="x")
    s = add_variable(session=s, key="token", value="abc123")
    assert s["variables"]["token"] == "abc123"

def test_interpolate():
    r = interpolate_variables(template="Bearer {{token}}", variables={"token": "abc"})
    assert r == "Bearer abc"

def test_history():
    s = create_session(developer_id="d1", app_id="a1", base_url="x")
    s = add_to_history(session=s, request={"method": "GET"}, response={"status": 200})
    assert len(s["history"]) == 1

def test_history_limit():
    s = {"history": [{"i": i} for i in range(60)]}
    s = add_to_history(session=s, request={}, response={})
    assert len(s["history"]) == 50
