from app.services.app_marketplace_app_marketplace_seo import build_page_seo, build_app_structured_data

def test_seo():
    s = build_page_seo(page_type="app", title="SuperApp", description="A great tool",
                         url="https://openskill.dev/marketplace/apps/super-app")
    assert "OpenSkill Marketplace" in s["title"]
    assert s["og"]["type"] == "website"

def test_structured():
    d = build_app_structured_data(app={"name": "App", "description": "Tool", "category": "connector"},
                                    rating=4.5, review_count=100)
    assert d["@type"] == "SoftwareApplication"
    assert d["aggregateRating"]["ratingValue"] == 4.5
