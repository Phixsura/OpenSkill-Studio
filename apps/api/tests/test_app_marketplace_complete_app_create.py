from app.services.app_marketplace_complete_app_create import build_app_create_flow, validate_app_name

def test_flow():
    f = build_app_create_flow(templates=[{"name": "Basic"}], categories=[{"id": "connector", "name": "Connectors"}])
    assert f["page_type"] == "create_app"
    assert len(f["methods"]) == 3
    assert len(f["form"]["fields"]) == 5

def test_name_valid():
    r = validate_app_name(name="My New App", existing_names=["Other App"])
    assert r["valid"]
    assert r["suggested_slug"] == "my-new-app"

def test_name_taken():
    r = validate_app_name(name="Existing App", existing_names=["existing app"])
    assert not r["valid"]

def test_name_short():
    r = validate_app_name(name="AB", existing_names=[])
    assert not r["valid"]
