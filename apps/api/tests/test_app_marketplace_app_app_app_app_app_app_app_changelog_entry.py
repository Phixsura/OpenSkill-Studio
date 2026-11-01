from app.services.app_marketplace_app_app_app_app_app_app_app_changelog_entry import create_entry, group_entries

def test_entry():
    e = create_entry(entry_type="added", title="SSO Support", description="SAML and OIDC", version="3.5")
    assert e["emoji"] == "✨"
    assert e["title"] == "SSO Support"
    assert e["color"] == "green"

def test_group():
    entries = [
        create_entry(entry_type="added", title="SSO"),
        create_entry(entry_type="fixed", title="Auth bug"),
        create_entry(entry_type="added", title="Dark mode"),
        create_entry(entry_type="removed", title="Legacy API", breaking=True),
    ]
    r = group_entries(entries)
    assert r["total"] == 4
    assert r["has_breaking"]
    assert r["sections"][0]["type"] == "added"
    assert r["sections"][0]["count"] == 2
