"""Quick start — the fastest path from zero to published app."""

QUICK_START_STEPS = [
    {"step": 1, "command": "npm install -g @openskill/cli", "description": "Install the CLI"},
    {"step": 2, "command": "openskill auth login", "description": "Authenticate"},
    {"step": 3, "command": "openskill apps create --template typescript-basic --name my-app", "description": "Create app"},
    {"step": 4, "command": "cd my-app && openskill dev", "description": "Start development"},
    {"step": 5, "command": "openskill test", "description": "Run tests"},
    {"step": 6, "command": "openskill apps submit --version 1.0.0", "description": "Submit for review"},
]


def get_quick_start() -> dict:
    return {"title": "Quick Start — 5 Minutes to Your First App",
            "steps": QUICK_START_STEPS, "total_time_min": 5,
            "prerequisites": ["Node.js 18+", "An OpenSkill account"]}


def get_step(*, step_number: int) -> dict | None:
    return next((s for s in QUICK_START_STEPS if s["step"] == step_number), None)
