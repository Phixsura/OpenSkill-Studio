"""API response formatter — standardized response shapes."""


def data_response(data: object) -> dict:
    """Format single-item response: { data: T }"""
    return {"data": data}


def list_response(data: list, *, total: int, page: int = 1, per_page: int = 20) -> dict:
    """Format list response: { data: T[], meta: {...} }"""
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1
    return {
        "data": data,
        "meta": {"total": total, "page": page, "per_page": per_page, "total_pages": total_pages},
    }


def error_response(code: str, message: str, *, status: int = 400, details: list | None = None) -> dict:
    """Format error response: { error: {...} }"""
    err = {"code": code, "message": message}
    if details:
        err["details"] = details
    return {"error": err}
