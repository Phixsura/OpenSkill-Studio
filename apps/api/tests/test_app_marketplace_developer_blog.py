from app.services.app_marketplace_developer_blog import build_blog_page, build_blog_post

def test_page():
    posts = [{"title": f"Post {i}", "category": "tutorial"} for i in range(25)]
    p = build_blog_page(posts=posts, page=2, per_page=10)
    assert len(p["posts"]) == 10
    assert p["pagination"]["total_pages"] == 3

def test_filter():
    posts = [{"title": "A", "category": "tutorial"}, {"title": "B", "category": "announcement"}]
    p = build_blog_page(posts=posts, category="tutorial")
    assert p["pagination"]["total"] == 1

def test_post():
    post = {"title": "Getting Started", "content": " ".join(["word"] * 600), "excerpt": "Learn how"}
    p = build_blog_post(post=post, related=[{"title": "Next Steps"}])
    assert p["read_time_min"] == 3
    assert "Getting Started" in p["seo"]["title"]
