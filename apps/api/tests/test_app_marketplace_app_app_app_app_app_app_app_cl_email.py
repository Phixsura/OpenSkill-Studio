from app.services.app_marketplace_app_app_app_app_app_app_app_cl_email import build_changelog_email

def test_email():
    r = build_changelog_email(subject="v3.5 Released!", version="3.5.0",
                                recipient_name="Alice", changes=[
                                    {"type": "added", "text": "SSO support"},
                                    {"type": "added", "text": "Dark mode"},
                                    {"type": "fixed", "text": "Login bug"},
                                ])
    assert r["greeting"] == "Hi Alice,"
    assert r["total_changes"] == 3
    assert len(r["sections"]) == 2  # added + fixed
    assert r["sections"][0]["count"] == 2  # 2 added
    assert r["preview_text"] == "3 changes in v3.5.0"
