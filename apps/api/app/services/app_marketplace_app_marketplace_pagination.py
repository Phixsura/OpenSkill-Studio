"""Marketplace pagination — standardized pagination for all list endpoints."""

def paginate(*, items: list, page: int = 1, per_page: int = 20) -> dict:
    total = len(items)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    page_items = items[start:start + per_page]
    return {"data": page_items, "meta": {"page": page, "per_page": per_page,
            "total": total, "total_pages": total_pages,
            "has_prev": page > 1, "has_next": page < total_pages}}

def build_page_links(*, base_url: str, page: int, total_pages: int) -> dict:
    links = {"self": f"{base_url}?page={page}"}
    if page > 1:
        links["prev"] = f"{base_url}?page={page - 1}"
        links["first"] = f"{base_url}?page=1"
    if page < total_pages:
        links["next"] = f"{base_url}?page={page + 1}"
        links["last"] = f"{base_url}?page={total_pages}"
    return links
