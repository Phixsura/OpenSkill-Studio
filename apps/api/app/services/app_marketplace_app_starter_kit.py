"""App starter kit — downloadable project scaffolding for new apps."""

STARTER_KITS = {
    "typescript-basic": {"name": "TypeScript Basic", "language": "typescript",
        "files": ["src/index.ts", "src/manifest.json", "package.json", "tsconfig.json", "README.md"],
        "dependencies": ["@openskill/sdk"], "dev_dependencies": ["typescript", "vitest"]},
    "python-basic": {"name": "Python Basic", "language": "python",
        "files": ["src/main.py", "manifest.json", "pyproject.toml", "README.md"],
        "dependencies": ["openskill-sdk"], "dev_dependencies": ["pytest"]},
    "typescript-webhook": {"name": "TypeScript Webhook Handler", "language": "typescript",
        "files": ["src/index.ts", "src/webhook.ts", "src/manifest.json", "package.json"],
        "dependencies": ["@openskill/sdk", "express"], "dev_dependencies": ["typescript", "vitest"]},
    "python-connector": {"name": "Python Connector", "language": "python",
        "files": ["src/connector.py", "src/auth.py", "manifest.json", "pyproject.toml"],
        "dependencies": ["openskill-sdk", "httpx"], "dev_dependencies": ["pytest"]},
}


def list_starter_kits(*, language: str | None = None) -> list[dict]:
    kits = [{"id": k, **v} for k, v in STARTER_KITS.items()]
    if language:
        kits = [k for k in kits if k["language"] == language]
    return kits


def get_starter_kit(*, kit_id: str) -> dict | None:
    kit = STARTER_KITS.get(kit_id)
    return {"id": kit_id, **kit} if kit else None


def scaffold_project(*, kit_id: str, app_name: str, app_slug: str) -> dict:
    kit = STARTER_KITS.get(kit_id)
    if not kit:
        return {"error": f"Unknown kit: {kit_id}"}
    return {"kit": kit_id, "app_name": app_name, "slug": app_slug,
            "files_created": kit["files"], "file_count": len(kit["files"]),
            "dependencies": kit["dependencies"], "next_steps": [
                f"cd {app_slug}", "npm install" if kit["language"] == "typescript" else "pip install -e .",
                "openskill dev", "openskill test"]}
