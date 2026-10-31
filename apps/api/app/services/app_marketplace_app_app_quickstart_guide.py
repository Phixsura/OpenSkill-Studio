"""Quickstart guide — step-by-step getting started content."""

import html

STEPS = [
    {"id": "install", "title": "Install the CLI", "code": "npm install -g @openskill/cli", "icon": "📦"},
    {"id": "login", "title": "Log in", "code": "osk login", "icon": "🔑"},
    {"id": "init", "title": "Create your app", "code": "osk init my-app", "icon": "🚀"},
    {"id": "develop", "title": "Start developing", "code": "cd my-app && osk dev", "icon": "💻"},
    {"id": "deploy", "title": "Deploy", "code": "osk deploy", "icon": "🌐"},
]


def build_quickstart(*, completed_steps: list[str] | None = None) -> dict:
    done = set(completed_steps or [])
    items = []
    for i, step in enumerate(STEPS):
        items.append({**step, "title": html.escape(step["title"]),
                       "order": i + 1, "completed": step["id"] in done})
    progress = round(len(done) / max(len(STEPS), 1) * 100)
    return {"steps": items, "total": len(items),
            "completed": len(done), "progress_pct": progress,
            "all_done": len(done) == len(STEPS),
            "next_step": next((s for s in items if not s["completed"]), None)}
