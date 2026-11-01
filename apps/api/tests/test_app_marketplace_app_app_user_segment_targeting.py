from app.services.app_marketplace_app_app_user_segment_targeting import match_segments, target_content

def test_match():
    user = {"id": "u1", "days_since_signup": 3, "actions_30d": 150, "plan": "pro", "is_developer": True}
    r = match_segments(user=user)
    assert "new_users" in r["segments"]
    assert "power_users" in r["segments"]
    assert "paying" in r["segments"]
    assert "developers" in r["segments"]

def test_target():
    rules = [
        {"content_id": "welcome_banner", "target_segments": ["new_users"]},
        {"content_id": "upgrade_prompt", "target_segments": ["power_users"], "exclude_segments": ["paying"]},
    ]
    r = target_content(content_rules=rules, user_segments=["new_users", "power_users", "paying"])
    assert "welcome_banner" in r["matched_content"]
    assert "upgrade_prompt" not in r["matched_content"]  # excluded
