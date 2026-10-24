"""Error boundary config — configure error boundary behavior."""


def build_error_boundary_config(*, app_name: str, show_details: bool = False,
                                   report_errors: bool = True) -> dict:
    return {
        "fallback": {
            "title": "Something went wrong",
            "message": f"An error occurred in {app_name}. Please try refreshing the page.",
            "icon": "💥",
            "actions": [
                {"label": "Refresh Page", "action": "reload"},
                {"label": "Go Home", "action": "navigate", "url": "/"},
            ],
        },
        "show_stack_trace": show_details,
        "report_to_service": report_errors,
        "retry_count": 3,
        "retry_delay_ms": 1000,
    }
