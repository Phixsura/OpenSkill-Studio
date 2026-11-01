from app.services.app_marketplace_extension_api_contract import (
    APIContractService, APIContract, ContractMethod, ContractStatus,
)

METHODS = [
    ContractMethod("getUser", {"required": ["user_id"], "properties": {"user_id": {"type": "string"}}},
                   {"properties": {"name": {"type": "string"}}}, "Get a user"),
    ContractMethod("listUsers", {"properties": {}}, {"properties": {"users": {"type": "array"}}}, "List users"),
]


def test_register_and_publish():
    svc = APIContractService()
    c = svc.register(APIContract("c1", "ext-1", 1, METHODS))
    assert c.status == ContractStatus.DRAFT
    assert svc.publish("ext-1", 1) is True
    assert svc.get_contract("ext-1", 1).status == ContractStatus.PUBLISHED


def test_get_latest():
    svc = APIContractService()
    svc.register(APIContract("c1", "ext-2", 1, METHODS))
    svc.register(APIContract("c2", "ext-2", 2, METHODS))
    svc.publish("ext-2", 1)
    svc.publish("ext-2", 2)
    latest = svc.get_latest("ext-2")
    assert latest.version == 2


def test_validate_call():
    svc = APIContractService()
    svc.register(APIContract("c1", "ext-3", 1, METHODS))
    svc.publish("ext-3", 1)
    ok, errors = svc.validate_call("ext-3", "getUser", {"user_id": "u1"})
    assert ok is True


def test_validate_missing_field():
    svc = APIContractService()
    svc.register(APIContract("c1", "ext-4", 1, METHODS))
    svc.publish("ext-4", 1)
    ok, errors = svc.validate_call("ext-4", "getUser", {})
    assert ok is False
    assert any("user_id" in e for e in errors)


def test_validate_wrong_type():
    svc = APIContractService()
    svc.register(APIContract("c1", "ext-5", 1, METHODS))
    svc.publish("ext-5", 1)
    ok, errors = svc.validate_call("ext-5", "getUser", {"user_id": 123})
    assert ok is False
    assert any("string" in e for e in errors)


def test_compatibility():
    svc = APIContractService()
    svc.register(APIContract("c1", "ext-6", 1, METHODS))
    svc.register(APIContract("c2", "ext-6", 2, [METHODS[0]]))  # removed listUsers
    compat = svc.check_compatibility("ext-6", 1, 2)
    assert compat["breaking"] is True
    assert "listUsers" in compat["methods_removed"]


def test_compatible_addition():
    svc = APIContractService()
    svc.register(APIContract("c1", "ext-7", 1, [METHODS[0]]))
    svc.register(APIContract("c2", "ext-7", 2, METHODS))  # added listUsers
    compat = svc.check_compatibility("ext-7", 1, 2)
    assert compat["compatible"] is True
    assert "listUsers" in compat["methods_added"]
