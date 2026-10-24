"""Developer blog — platform blog with tutorials, announcements, and case studies."""


def build_blog_page(*, posts: list[dict], page: int = 1, per_page: int = 10,
                       category: str | None = None) -> dict:
    filtered = posts
    if category:
        filtered = [p for p in filtered if p.get("category") == category]
    total = len(filtered)
    start = (page - 1) * per_page
    page_posts = filtered[start:start + per_page]
    return {
        "page_type": "blog",
        "posts": page_posts,
        "pagination": {"page": page, "total": total,
                         "total_pages": max(1, (total + per_page - 1) // per_page)},
        "categories": ["tutorial", "announcement", "case_study", "engineering", "community"],
        "active_category": category,
    }


def build_blog_post(*, post: dict, related: list[dict]) -> dict:
    read_time = max(1, len(post.get("content", "").split()) // 200)
    return {
        "post": post, "read_time_min": read_time,
        "related_posts": related[:3],
        "seo": {"title": f"{post.get('title', '')} — OpenSkill Blog",
                "description": post.get("excerpt", "")[:160]},
    }
