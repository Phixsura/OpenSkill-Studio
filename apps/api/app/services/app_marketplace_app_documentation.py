"""App documentation — manage structured docs for marketplace apps."""


def create_doc_page(*, app_id: str, slug: str, title: str, content: str,
                      order: int = 0, parent_slug: str | None = None) -> dict:
    if len(title) < 3:
        return {"error": "Title too short"}
    if len(content) < 20:
        return {"error": "Content too short (min 20 chars)"}
    return {
        "app_id": app_id, "slug": slug, "title": title, "content": content,
        "order": order, "parent_slug": parent_slug, "error": None,
    }


def build_doc_sidebar(*, pages: list[dict]) -> list[dict]:
    roots = [p for p in pages if not p.get("parent_slug")]
    roots.sort(key=lambda p: p.get("order", 0))
    tree = []
    for root in roots:
        children = sorted([p for p in pages if p.get("parent_slug") == root["slug"]],
                          key=lambda p: p.get("order", 0))
        tree.append({
            "slug": root["slug"], "title": root["title"],
            "children": [{"slug": c["slug"], "title": c["title"]} for c in children],
        })
    return tree


def search_docs(*, pages: list[dict], query: str) -> list[dict]:
    q = query.lower()
    results = []
    for p in pages:
        score = 0
        if q in p.get("title", "").lower():
            score += 10
        if q in p.get("content", "").lower():
            score += 5
        if score > 0:
            results.append({"slug": p["slug"], "title": p["title"], "score": score})
    return sorted(results, key=lambda r: -r["score"])
