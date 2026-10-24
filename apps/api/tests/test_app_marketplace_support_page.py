from app.services.app_marketplace_support_page import build_support_page, search_faq

def test_full():
    p = build_support_page(app={"name": "MyApp"},
                             faq=[{"question": "How?", "answer": "Like this."}],
                             contact={"email": "help@app.com", "response_time": "24h"},
                             docs_url="/docs", community_url="/community")
    assert p["section_count"] == 4
    assert p["has_faq"]
    assert p["has_docs"]

def test_minimal():
    p = build_support_page(app={"name": "App"}, faq=[], contact={"email": "x@y.com"},
                             docs_url=None, community_url=None)
    assert p["section_count"] == 1  # only contact
    assert not p["has_faq"]

def test_search():
    faq = [{"question": "How to install?", "answer": "Click install"},
           {"question": "Pricing?", "answer": "Free tier available"}]
    r = search_faq(faq=faq, query="install")
    assert len(r) == 1
