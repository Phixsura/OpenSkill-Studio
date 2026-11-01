from app.services.app_marketplace_developer_profile_v2 import validate_profile, compute_profile_completeness, build_profile_card

def test_valid():
    r = validate_profile(profile={"display_name": "DevCo", "slug": "devco", "support_email": "help@dev.co", "bio": "We build tools"})
    assert r["valid"]

def test_invalid_slug():
    r = validate_profile(profile={"display_name": "DevCo", "slug": "A B C"})
    assert not r["valid"]

def test_invalid_email():
    r = validate_profile(profile={"display_name": "DevCo", "slug": "devco", "support_email": "not-email"})
    assert not r["valid"]

def test_completeness():
    r = compute_profile_completeness(profile={"display_name": "X", "slug": "x", "bio": "B"})
    assert r["completeness_pct"] == 45  # 20 + 10 + 15
    assert not r["complete"]
    assert "support_email" in r["missing"]

def test_card():
    c = build_profile_card(profile={"display_name": "DevCo", "slug": "devco", "bio": "Tools", "verified": True, "created_at": "2024-01-01"},
                             stats={"apps": 5, "installs": 2000, "avg_rating": 4.5})
    assert c["name"] == "DevCo"
    assert c["stats"]["apps"] == 5
