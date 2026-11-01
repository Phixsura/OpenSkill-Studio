from app.services.app_marketplace_developer_community_page import build_community_page, build_discussion_detail

def test_page():
    discussions = [{"title": "Pinned", "pinned": True}, {"title": "Recent", "pinned": False}]
    p = build_community_page(discussions=discussions, popular_tags=[{"tag": "webhook"}],
                               members_count=500, online_count=25)
    assert p["stats"]["members"] == 500
    assert len(p["pinned"]) == 1
    assert len(p["categories"]) == 5

def test_detail():
    d = build_discussion_detail(discussion={"title": "Help with OAuth"},
                                  replies=[{"body": "Try PKCE"}])
    assert d["reply_count"] == 1
    assert d["can_reply"]
