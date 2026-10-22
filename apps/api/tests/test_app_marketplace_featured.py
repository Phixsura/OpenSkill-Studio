from app.services.app_marketplace_featured import set_featured, get_featured, add_featured, remove_featured

def test_set_and_get():
    set_featured([{"id": "a1"}, {"id": "a2"}])
    f = get_featured()
    assert len(f) == 2

def test_limit():
    set_featured([{"id": f"a{i}"} for i in range(10)])
    assert len(get_featured(limit=3)) == 3

def test_add():
    set_featured([])
    add_featured("new_app", reason="Great app")
    assert len(get_featured()) == 1

def test_remove():
    set_featured([{"id": "a1"}, {"id": "a2"}])
    assert remove_featured("a1") is True
    assert len(get_featured()) == 1

def test_remove_missing():
    set_featured([])
    assert remove_featured("nonexist") is False
