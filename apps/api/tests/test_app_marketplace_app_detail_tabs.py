from app.services.app_marketplace_app_detail_tabs import build_overview_tab, build_reviews_tab, build_changelog_tab, build_all_tabs

def test_overview():
    t = build_overview_tab(app={"description": "Great app", "category": "connector"},
                            developer={"display_name": "DevCo"}, screenshots=["s1.png"])
    assert t["key"] == "overview"
    assert t["content"]["developer"] == "DevCo"

def test_reviews():
    t = build_reviews_tab(reviews=[{"rating": 5}], stats={"count": 100, "avg_rating": 4.5})
    assert "100" in t["title"]
    assert t["content"]["avg_rating"] == 4.5

def test_changelog():
    t = build_changelog_tab(versions=[{"version": "2.0"}, {"version": "1.0"}])
    assert t["content"]["latest"]["version"] == "2.0"

def test_all():
    tabs = build_all_tabs(app={"description": "D"}, developer={"display_name": "D"},
                           screenshots=[], reviews=[], review_stats={"count": 0},
                           versions=[], support_email="help@x.com", docs_url="/docs", faq=[])
    assert len(tabs) == 4
    assert tabs[3]["content"]["has_email"]
