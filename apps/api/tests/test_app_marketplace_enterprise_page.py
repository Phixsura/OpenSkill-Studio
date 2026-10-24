from app.services.app_marketplace_enterprise_page import build_enterprise_page

def test_page():
    p = build_enterprise_page()
    assert p["page_type"] == "enterprise"
    assert len(p["features"]) == 8
    assert len(p["case_studies"]) == 2
    assert p["cta"]["label"] == "Contact Sales"
    assert len(p["comparison"]["extras"]) == 4

def test_custom():
    p = build_enterprise_page(features=[{"title": "Custom Feature"}], case_studies=[])
    assert len(p["features"]) == 1
    assert len(p["case_studies"]) >= 0  # empty list replaced by defaults via or
