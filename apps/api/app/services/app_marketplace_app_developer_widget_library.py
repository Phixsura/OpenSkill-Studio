"""Widget library — reusable UI widget catalog for app extensions."""

WIDGETS = [
    {"id": "stat-card", "name": "Stat Card", "category": "display", "preview": "📊"},
    {"id": "data-table", "name": "Data Table", "category": "display", "preview": "📋"},
    {"id": "form-builder", "name": "Form Builder", "category": "input", "preview": "📝"},
    {"id": "chart-bar", "name": "Bar Chart", "category": "charts", "preview": "📊"},
    {"id": "chart-line", "name": "Line Chart", "category": "charts", "preview": "📈"},
    {"id": "notification", "name": "Notification", "category": "feedback", "preview": "🔔"},
    {"id": "modal", "name": "Modal Dialog", "category": "overlay", "preview": "🪟"},
    {"id": "dropdown", "name": "Dropdown Menu", "category": "input", "preview": "📃"},
]


def list_widgets(*, category: str | None = None) -> list[dict]:
    if category:
        return [w for w in WIDGETS if w["category"] == category]
    return WIDGETS


def get_widget(*, widget_id: str) -> dict | None:
    return next((w for w in WIDGETS if w["id"] == widget_id), None)


def get_widget_categories() -> list[dict]:
    cats: dict[str, int] = {}
    for w in WIDGETS:
        cats[w["category"]] = cats.get(w["category"], 0) + 1
    return [{"category": c, "count": n} for c, n in sorted(cats.items())]
