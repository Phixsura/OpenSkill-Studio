"""UI extension surface registry."""

SURFACES = {
    "dashboard_card": {"label": "Dashboard Card", "max_width": 600, "max_height": 400},
    "project_sidebar": {"label": "Project Sidebar", "max_width": 400, "max_height": 800},
    "submission_panel": {"label": "Submission Panel", "max_width": 800, "max_height": 600},
    "settings_tab": {"label": "Settings Tab", "max_width": 1200, "max_height": 800},
    "cohort_widget": {"label": "Cohort Widget", "max_width": 500, "max_height": 300},
    "portfolio_section": {"label": "Portfolio Section", "max_width": 800, "max_height": 600},
    "evaluation_panel": {"label": "Evaluation Panel", "max_width": 800, "max_height": 600},
    "marketplace_banner": {"label": "Marketplace Banner", "max_width": 1200, "max_height": 200},
}

def get_surface(name: str) -> dict | None:
    return SURFACES.get(name)

def list_surfaces() -> list[str]:
    return sorted(SURFACES.keys())
