from app.services.app_marketplace_app_app_app_app_app_app_app_contract_reg import ContractRegistry

def test_register():
    cr = ContractRegistry()
    cr.register("user-api", "1.0", {"fields": {"id": "string"}}, "team-a")
    cr.register("user-api", "2.0", {"fields": {"id": "string", "email": "string"}})
    assert cr.latest("user-api")["version"] == "2.0"
    assert cr.versions("user-api") == ["1.0", "2.0"]

def test_search():
    cr = ContractRegistry()
    cr.register("user-api", "1.0", {})
    cr.register("order-api", "1.0", {})
    r = cr.search("user")
    assert len(r) == 1
    assert r[0]["name"] == "user-api"
    assert cr.stats()["contracts"] == 2
