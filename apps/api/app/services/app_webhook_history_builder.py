"""Webhook history builder — compile webhook delivery history page."""

def build_webhook_history_page(*, deliveries: list[dict], total: int, page: int, per_page: int,
                                  success_rate: float) -> dict:
    return {
        "deliveries": deliveries,
        "total": total, "page": page, "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 1,
        "success_rate": round(success_rate, 1),
    }
