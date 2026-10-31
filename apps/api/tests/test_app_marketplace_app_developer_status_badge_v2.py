from app.services.app_marketplace_app_developer_status_badge_v2 import generate_badge_url, compute_badge_data, generate_markdown_badges

def test_url():
    u = generate_badge_url(app_slug="my-app", metric="installs", value="500", color="blue")
    assert "my-app" in u
    assert "installs" in u

def test_badge_data():
    b = compute_badge_data(app={"status": "published", "install_count": 500, "avg_rating": 4.5})
    assert len(b) == 3
    assert b[0]["value"] == "published"
    assert b[0]["color"] == "green"

def test_markdown():
    badges = [{"metric": "status", "value": "published", "color": "green"}]
    md = generate_markdown_badges(app_slug="my-app", badges=badges)
    assert "![status]" in md
    assert "my-app" in md
