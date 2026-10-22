"""App scaffold generator — generate starter files for new apps.

Creates the initial directory structure, manifest, and boilerplate
code for a new developer app.
"""

import json

FILE_TEMPLATES = {
    "connector": {
        "manifest.json": None,  # Generated from manifest_template
        "src/index.py": '''"""OpenSkill Connector — {name}"""

import os
from openskill_sdk import OpenSkillClient


async def on_submission_completed(event: dict) -> dict:
    """Handle submission.completed events."""
    submission_id = event["data"]["id"]
    # TODO: Implement your connector logic
    return {{"status": "processed", "submission_id": submission_id}}


async def health_check() -> dict:
    return {{"status": "healthy"}}
''',
        "tests/test_connector.py": '''"""Test suite for {slug} connector."""

def test_health():
    # TODO: Add tests
    assert True
''',
        "README.md": "# {name}\n\nOpenSkill Connector\n\n## Setup\n\n1. Set `API_KEY` secret\n2. Configure `base_url`\n",
    },
    "automation": {
        "manifest.json": None,
        "src/index.js": '''// OpenSkill Automation — {name}

export async function onSubmissionCompleted(event) {{
  const submissionId = event.data.id;
  // TODO: Implement automation logic
  return {{ status: "processed" }};
}}
''',
        "README.md": "# {name}\n\nOpenSkill Automation\n",
    },
}


def generate_scaffold(*, name: str, slug: str, category: str) -> dict[str, str]:
    """Generate scaffold files for a new app.
    
    Returns {path: content} mapping.
    """
    templates = FILE_TEMPLATES.get(category, FILE_TEMPLATES["connector"])
    files = {}
    for path, content in templates.items():
        if content is None:
            continue  # Manifest generated separately
        files[path] = content.format(name=name, slug=slug)
    return files


def list_scaffold_types() -> list[dict]:
    """List available scaffold types."""
    return [{"category": cat, "files": list(templates.keys())} for cat, templates in FILE_TEMPLATES.items()]
