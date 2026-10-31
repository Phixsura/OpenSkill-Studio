from app.services.app_developer_app_publishing_page_builder import build_publishing_page

def test_ready():
    p = build_publishing_page(app={"name": "X"}, can_publish=True, errors=[], warnings=[])
    assert p["ready"] is True

def test_not_ready():
    p = build_publishing_page(app={"name": "X"}, can_publish=False, errors=["Missing desc"], warnings=[])
    assert p["ready"] is False
    assert p["steps_remaining"] == 1
