from app.services.app_marketplace_app_email_digest import build_weekly_digest

def test_digest():
    stats = {"new_installs": 150, "install_change_pct": 12.5, "revenue": 2500.50,
             "revenue_change_pct": 8.3, "new_reviews": 10, "avg_rating": 4.6}
    r = build_weekly_digest(developer_name="Alice", period="Oct 16-22",
        stats=stats, highlights=["App hit 1K installs!", "New 5-star review"])
    assert "Alice" in r["subject"]
    assert len(r["sections"]) == 4
    assert len(r["highlights"]) == 2

def test_xss():
    r = build_weekly_digest(developer_name="<script>alert(1)</script>",
        period="Oct", stats={"new_installs": 1}, highlights=["<b>test</b>"])
    assert "<script>" not in r["subject"]
    assert "<b>" not in r["highlights"][0]

def test_empty_stats():
    r = build_weekly_digest(developer_name="Bob", period="Oct", stats={}, highlights=[])
    assert len(r["sections"]) == 0
