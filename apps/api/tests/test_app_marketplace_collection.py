from app.services.app_marketplace_collection import create_collection, get_collection, list_collections, add_to_collection

def test_create():
    c = create_collection(slug="best-connectors", title="Best Connectors", description="Top rated", app_ids=["a1", "a2"])
    assert c["app_count"] == 2

def test_get():
    create_collection(slug="get-test", title="T", description="D", app_ids=[])
    assert get_collection("get-test") is not None

def test_list():
    create_collection(slug="list-a", title="A", description="", app_ids=[])
    create_collection(slug="list-b", title="B", description="", app_ids=[])
    assert len(list_collections()) >= 2

def test_add():
    create_collection(slug="add-test", title="T", description="D", app_ids=["a1"])
    add_to_collection("add-test", "a2")
    assert get_collection("add-test")["app_count"] == 2

def test_add_nonexistent():
    assert add_to_collection("nope", "a1") is False
