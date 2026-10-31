"""SDK quickstart — language-specific SDK setup guides."""

import html

SDK_GUIDES = {
    "typescript": {
        "install": "npm install @openskill/sdk",
        "import": "import { OpenSkill } from '@openskill/sdk';",
        "init": "const client = new OpenSkill({ apiKey: process.env.OSK_API_KEY });",
        "example": "const apps = await client.apps.list();\nconsole.log(`Found ${apps.length} apps`);",
        "run": "npx tsx index.ts",
    },
    "python": {
        "install": "pip install openskill-sdk",
        "import": "from openskill import OpenSkill",
        "init": 'client = OpenSkill(api_key=os.environ["OSK_API_KEY"])',
        "example": 'apps = client.apps.list()\nprint(f"Found {len(apps)} apps")',
        "run": "python main.py",
    },
}


def build_sdk_quickstart(*, language: str = "typescript") -> dict:
    guide = SDK_GUIDES.get(language, SDK_GUIDES["typescript"])
    steps = [
        {"order": 1, "title": "Install", "code": guide["install"]},
        {"order": 2, "title": "Import", "code": guide["import"]},
        {"order": 3, "title": "Initialize", "code": guide["init"]},
        {"order": 4, "title": "Use", "code": guide["example"]},
        {"order": 5, "title": "Run", "code": guide["run"]},
    ]
    return {"language": language, "steps": steps, "step_count": len(steps),
            "available_languages": list(SDK_GUIDES.keys())}
