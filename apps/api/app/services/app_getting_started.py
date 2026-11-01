"""Getting started — structured guide data for new developers."""

GUIDE_STEPS = [
    {"step": 1, "title": "Create Developer Account", "description": "Set up your developer profile with name, slug, and contact email.", "docs_url": "/docs/developer/accounts"},
    {"step": 2, "title": "Create Your First App", "description": "Choose a category (connector, automation, analytics, etc.) and configure your app.", "docs_url": "/docs/developer/apps"},
    {"step": 3, "title": "Write Your Manifest", "description": "Define permissions, sandbox config, events, and UI extensions in manifest.json.", "docs_url": "/docs/developer/manifest"},
    {"step": 4, "title": "Build & Test", "description": "Use the SDK to build your app and test in the sandbox environment.", "docs_url": "/docs/developer/sdk"},
    {"step": 5, "title": "Submit for Review", "description": "Submit your app version for automated and manual review.", "docs_url": "/docs/developer/review"},
    {"step": 6, "title": "Publish to Marketplace", "description": "Once approved, publish your app to the marketplace.", "docs_url": "/docs/developer/publish"},
]


def get_guide() -> list[dict]:
    return GUIDE_STEPS


def get_current_step(completed: set[int]) -> dict | None:
    for step in GUIDE_STEPS:
        if step["step"] not in completed:
            return step
    return None
