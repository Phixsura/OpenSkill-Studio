from app.services.app_marketplace_extension_playground_history import PlaygroundHistoryService


def test_save_and_history():
    svc = PlaygroundHistoryService()
    svc.save_request("u1", "List users", "GET", "/api/users", status=200)
    svc.save_request("u1", "Create user", "POST", "/api/users", body='{"name":"Alice"}', status=201)
    history = svc.get_history("u1")
    assert len(history) == 2


def test_collections():
    svc = PlaygroundHistoryService()
    req = svc.save_request("u1", "Test", "GET", "/api/test")
    col = svc.create_collection("u1", "User API Tests")
    assert svc.add_to_collection("u1", col.collection_id, req.request_id) is True
    assert len(col.requests) == 1


def test_search():
    svc = PlaygroundHistoryService()
    svc.save_request("u1", "List users", "GET", "/api/users")
    svc.save_request("u1", "Get item", "GET", "/api/items/1")
    results = svc.search("u1", "users")
    assert len(results) == 1


def test_delete():
    svc = PlaygroundHistoryService()
    req = svc.save_request("u1", "Temp", "GET", "/temp")
    assert svc.delete_request("u1", req.request_id) is True
    assert len(svc.get_history("u1")) == 0


def test_no_duplicate_in_collection():
    svc = PlaygroundHistoryService()
    req = svc.save_request("u1", "T", "GET", "/t")
    col = svc.create_collection("u1", "C")
    svc.add_to_collection("u1", col.collection_id, req.request_id)
    svc.add_to_collection("u1", col.collection_id, req.request_id)
    assert len(col.requests) == 1
