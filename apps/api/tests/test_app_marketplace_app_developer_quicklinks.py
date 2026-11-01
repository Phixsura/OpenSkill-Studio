from app.services.app_marketplace_app_developer_quicklinks import get_quicklinks

def test_with_apps():
    links = get_quicklinks(developer={"verified": True}, apps=[{"id": "a1", "name": "MyApp"}])
    labels = [l["label"] for l in links]
    assert "Edit MyApp" in labels
    assert "Analytics Dashboard" in labels

def test_no_apps():
    links = get_quicklinks(developer={"verified": False}, apps=[])
    assert links[0]["label"] == "Create New App"
    assert not any("Analytics" in l["label"] for l in links)
