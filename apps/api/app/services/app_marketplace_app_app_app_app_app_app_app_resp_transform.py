"""API response transformer — transform API responses between formats."""
from __future__ import annotations


def transform_response(response: dict, format_type: str = "standard") -> dict:
    if format_type == "standard":
        return {"data": response.get("result", response), "meta": {"format": "standard"}}
    elif format_type == "envelope":
        return {"success": True, "data": response.get("result", response),
                "error": None, "meta": {"format": "envelope"}}
    elif format_type == "flat":
        return response.get("result", response)
    return response


def paginate_response(items: list, page: int = 1, per_page: int = 20) -> dict:
    total = len(items)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    return {"data": items[start:end], "meta": {"page": page, "per_page": per_page,
            "total": total, "total_pages": total_pages,
            "has_next": page < total_pages, "has_prev": page > 1}}
