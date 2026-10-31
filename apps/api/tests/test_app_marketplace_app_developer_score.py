from app.services.app_marketplace_app_developer_score import compute_developer_score

def test_high():
    r = compute_developer_score(apps_published=5, avg_rating=4.8, total_installs=5000, reviews_replied=10, bugs_fixed=5)
    assert r["tier"] in ("gold", "platinum")

def test_newcomer():
    r = compute_developer_score(apps_published=0, avg_rating=0, total_installs=0, reviews_replied=0, bugs_fixed=0)
    assert r["tier"] == "newcomer"
