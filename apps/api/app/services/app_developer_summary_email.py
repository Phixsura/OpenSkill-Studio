"""Developer summary email — build weekly email content."""

def build_summary_email(*, developer_name: str, app_count: int, total_installs_week: int, total_errors_week: int) -> dict:
    return {
        "subject": f"Weekly Summary: {app_count} apps, {total_installs_week} new installs",
        "greeting": f"Hi {developer_name},",
        "stats": {"apps": app_count, "new_installs": total_installs_week, "errors": total_errors_week},
        "cta": {"label": "View Dashboard", "url": "/dashboard/developer"},
    }
