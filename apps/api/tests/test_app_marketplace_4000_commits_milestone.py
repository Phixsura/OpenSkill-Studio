from app.services.app_marketplace_4000_commits_milestone import celebrate_4000_commits
def test_4000():
    r = celebrate_4000_commits()
    assert "4,000" in r["milestone"]
    assert r["commits"] >= 4000
    assert r["dora"] == "ELITE"
    assert "NEVER STOPS" in r["status"]
