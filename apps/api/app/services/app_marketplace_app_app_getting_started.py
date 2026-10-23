"""Getting started — quick start guide with code examples."""

import html

CODE_EXAMPLES = {
    "typescript": {
        "install": "npm install @openskill/sdk",
        "init": '''import { OpenSkill } from '@openskill/sdk';

const client = new OpenSkill({ apiKey: process.env.OSK_API_KEY });

const apps = await client.apps.list();
console.log(`Found ${apps.length} apps`);''',
    },
    "python": {
        "install": "pip install openskill-sdk",
        "init": '''from openskill import OpenSkill

client = OpenSkill(api_key=os.environ["OSK_API_KEY"])

apps = client.apps.list()
print(f"Found {len(apps)} apps")''',
    },
}


def build_getting_started(*, language: str = "typescript") -> dict:
    examples = CODE_EXAMPLES.get(language, CODE_EXAMPLES["typescript"])
    return {
        "language": language,
        "install_command": examples["install"],
        "code_example": examples["init"],
        "steps": [
            {"order": 1, "title": "Install the SDK", "code": examples["install"]},
            {"order": 2, "title": "Set up your API key", "code": f"export OSK_API_KEY=your_key_here"},
            {"order": 3, "title": "Write your first integration", "code": examples["init"]},
            {"order": 4, "title": "Run it!", "code": "npx tsx index.ts" if language == "typescript" else "python main.py"},
        ],
        "available_languages": list(CODE_EXAMPLES.keys()),
    }
