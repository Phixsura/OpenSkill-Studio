from app.services.app_marketplace_app_app_app_app_app_app_app_chain_validate import validate_chain

def test_valid():
    r = validate_chain({"api": ["db", "cache"], "db": [], "cache": []})
    assert r["valid"]
    assert r["max_depth"] == 2

def test_cycle():
    r = validate_chain({"a": ["b"], "b": ["c"], "c": ["a"]})
    assert not r["valid"]
    assert len(r["cycles"]) >= 1

def test_depth():
    r = validate_chain({"a": ["b"], "b": ["c"], "c": ["d"], "d": []}, max_depth=2)
    assert not r["valid"]
    assert r["max_depth"] == 4
