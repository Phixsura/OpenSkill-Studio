from app.services.app_marketplace_copy_text import get_copy, get_copy_with_params, get_all_copy

def test_get():
    assert get_copy(key="cta_install") == "Install App"

def test_fallback():
    assert get_copy(key="nonexistent", fallback="Default") == "Default"

def test_with_params():
    # Template not parameterized in current copy, but function works
    r = get_copy_with_params(key="cta_install", params={})
    assert r == "Install App"

def test_all():
    c = get_all_copy()
    assert len(c) >= 20

def test_prefix():
    c = get_all_copy(prefix="cta_")
    assert all(k.startswith("cta_") for k in c)
    assert len(c) >= 6

def test_empty_prefix():
    c = get_all_copy(prefix="empty_")
    assert len(c) >= 4
