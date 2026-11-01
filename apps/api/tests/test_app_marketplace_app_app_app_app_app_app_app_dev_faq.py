from app.services.app_marketplace_app_app_app_app_app_app_app_dev_faq import search_faq, get_by_category, list_categories

def test_search():
    r = search_faq("api key")
    assert len(r) >= 1
    assert any("API key" in f["question"] for f in r)

def test_category():
    r = get_by_category("api")
    assert len(r) >= 1

def test_categories():
    cats = list_categories()
    assert "api" in cats
    assert "webhooks" in cats
