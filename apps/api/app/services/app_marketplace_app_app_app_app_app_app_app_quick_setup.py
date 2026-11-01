"""App quick setup — minimal config for getting an app running fast."""
from __future__ import annotations
import secrets
import html


def generate_quick_setup(*, app_name: str, language: str = "typescript") -> dict:
    api_key = f"sk_test_{secrets.token_urlsafe(16)}"
    safe_name = html.escape(app_name)
    install_cmds = {
        "typescript": f"npm install @openskill/sdk",
        "python": f"pip install openskill-sdk",
        "go": f"go get github.com/openskill/sdk-go",
    }
    code_snippets = {
        "typescript": f'import {{ OpenSkill }} from "@openskill/sdk";\nconst client = new OpenSkill({{ apiKey: "{api_key}" }});',
        "python": f'from openskill import OpenSkill\nclient = OpenSkill(api_key="{api_key}")',
        "go": f'client := openskill.New("{api_key}")',
    }
    return {
        "app_name": safe_name, "language": language,
        "api_key": api_key,
        "install": install_cmds.get(language, install_cmds["typescript"]),
        "code": code_snippets.get(language, code_snippets["typescript"]),
        "next_steps": ["Configure webhooks", "Set up deployment", "Add team members"],
        "estimated_time": "5 minutes",
    }
