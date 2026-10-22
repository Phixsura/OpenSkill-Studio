from app.services.app_developer_app_review_page_builder import build_review_page

def test_submitted():
    p = build_review_page(app={"name": "X"}, version={"version": "1.0"}, review={"review_status": "pending", "reviewer_id": "r1"})
    assert p["submitted"] is True
    assert p["review_status"] == "pending"

def test_not_submitted():
    p = build_review_page(app={"name": "X"}, version={"version": "1.0"}, review=None)
    assert p["submitted"] is False
