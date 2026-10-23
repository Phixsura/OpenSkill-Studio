from app.services.app_marketplace_app_app_app_app_app_app_app_color_mode import get_mode, resolve_mode, list_modes

def test_mode():
    m = get_mode("dark")
    assert m["icon"] == "🌙"
    assert m["bg"] == "#111827"

def test_resolve():
    r = resolve_mode("system", system_dark=True)
    assert r["resolved"] == "dark"
    r2 = resolve_mode("system", system_dark=False)
    assert r2["resolved"] == "light"
    r3 = resolve_mode("dark")
    assert r3["resolved"] == "dark"

def test_list():
    assert len(list_modes()) == 3
