"""App skeleton — scaffold new app project structure."""

import html


def generate_skeleton(*, app_name: str, runtime: str = "node",
                        features: list[str] | None = None) -> dict:
    feat_set = set(features or [])
    files = [
        {"path": "package.json" if runtime == "node" else "pyproject.toml", "type": "config"},
        {"path": "README.md", "type": "docs"},
        {"path": ".gitignore", "type": "config"},
        {"path": "src/index.ts" if runtime == "node" else "src/main.py", "type": "source"},
    ]
    if "tests" in feat_set:
        files.append({"path": "tests/index.test.ts" if runtime == "node" else "tests/test_main.py", "type": "test"})
    if "docker" in feat_set:
        files.append({"path": "Dockerfile", "type": "config"})
        files.append({"path": "docker-compose.yml", "type": "config"})
    if "ci" in feat_set:
        files.append({"path": ".github/workflows/ci.yml", "type": "ci"})
    if "webhooks" in feat_set:
        files.append({"path": "src/webhooks.ts" if runtime == "node" else "src/webhooks.py", "type": "source"})
    return {"app_name": html.escape(app_name), "runtime": runtime,
            "files": files, "file_count": len(files),
            "features": list(feat_set)}
