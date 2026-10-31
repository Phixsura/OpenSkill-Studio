from app.services.app_surface_registry import get_surface, list_surfaces, SURFACES

def test_get():
    s = get_surface("dashboard_card")
    assert s is not None and "max_width" in s

def test_unknown():
    assert get_surface("x") is None

def test_list():
    assert len(list_surfaces()) == len(SURFACES)

def test_count():
    assert len(SURFACES) >= 7
