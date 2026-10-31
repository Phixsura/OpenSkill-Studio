"""Sandbox page builder — compile sandbox config + execution page."""

def build_sandbox_page(*, sandbox_config: dict | None, recent_executions: list[dict], total_executions: int) -> dict:
    return {"configured": sandbox_config is not None, "config": sandbox_config,
            "recent_executions": recent_executions[:10], "total_executions": total_executions}
