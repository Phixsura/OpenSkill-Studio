from app.services.app_marketplace_app_app_app_app_app_app_app_atom_feed import build_atom_feed, generate_atom_xml

def test_feed():
    f = build_atom_feed(title="My App Changelog", app_id="myapp", entries=[
        {"title": "v2.0 Released", "version": "2.0.0", "date": "2026-10-24", "summary": "Major update"},
        {"title": "v1.5 Patch", "version": "1.5.1", "date": "2026-10-20", "summary": "Bug fixes"},
    ])
    assert f["item_count"] == 2
    assert f["content_type"] == "application/atom+xml"
    assert f["updated"] == "2026-10-24"

def test_xml():
    f = build_atom_feed(title="Test", app_id="t", entries=[{"title": "v1", "version": "1.0", "date": "2026-01-01"}])
    xml = generate_atom_xml(f)
    assert "<?xml" in xml
    assert "<feed" in xml
    assert "<entry>" in xml
