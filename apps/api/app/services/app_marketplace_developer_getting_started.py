"""Developer getting started — guided tutorial for new developers."""

TUTORIAL_STEPS = [
    {"step": 1, "title": "Set Up Your Environment", "duration_min": 5,
     "content": "Install the OpenSkill CLI and authenticate.",
     "commands": ["npm install -g @openskill/cli", "openskill auth login"]},
    {"step": 2, "title": "Create Your First App", "duration_min": 10,
     "content": "Use a starter kit to scaffold your app.",
     "commands": ["openskill apps create --template typescript-basic --name my-app"]},
    {"step": 3, "title": "Add Your Logic", "duration_min": 15,
     "content": "Implement your app's core functionality.",
     "commands": ["cd my-app", "code src/index.ts"]},
    {"step": 4, "title": "Test in Sandbox", "duration_min": 10,
     "content": "Run your app in the sandbox to verify it works.",
     "commands": ["openskill dev", "openskill test"]},
    {"step": 5, "title": "Submit for Review", "duration_min": 5,
     "content": "Submit your app for marketplace review.",
     "commands": ["openskill apps submit --version 1.0.0"]},
]


def get_tutorial() -> dict:
    total_min = sum(s["duration_min"] for s in TUTORIAL_STEPS)
    return {"title": "Getting Started with OpenSkill", "steps": TUTORIAL_STEPS,
            "total_steps": len(TUTORIAL_STEPS), "total_duration_min": total_min}


def get_tutorial_step(*, step_number: int) -> dict | None:
    return next((s for s in TUTORIAL_STEPS if s["step"] == step_number), None)


def compute_tutorial_progress(*, completed_steps: list[int]) -> dict:
    total = len(TUTORIAL_STEPS)
    done = sum(1 for s in TUTORIAL_STEPS if s["step"] in completed_steps)
    return {"completed": done, "total": total, "pct": round(done / total * 100),
            "next_step": next((s["step"] for s in TUTORIAL_STEPS if s["step"] not in completed_steps), None),
            "all_done": done >= total}
