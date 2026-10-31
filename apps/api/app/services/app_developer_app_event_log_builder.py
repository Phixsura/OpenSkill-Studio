"""Event log builder — compile event log page for app detail."""

def build_event_log_page(*, events: list[dict], total: int, page: int, per_page: int) -> dict:
    return {"events": events, "total": total, "page": page, "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 1}
