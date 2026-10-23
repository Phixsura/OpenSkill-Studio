"""SDK quickstart generator — generate getting-started code for different languages."""
from __future__ import annotations

TEMPLATES = {
    "typescript": {
        "install": "npm install @openskill/sdk",
        "code": '''import { OpenSkill } from "@openskill/sdk";

const client = new OpenSkill({ apiKey: "YOUR_API_KEY" });

const apps = await client.apps.list();
console.log(apps);''',
    },
    "python": {
        "install": "pip install openskill-sdk",
        "code": '''from openskill import OpenSkill

client = OpenSkill(api_key="YOUR_API_KEY")

apps = client.apps.list()
print(apps)''',
    },
    "go": {
        "install": "go get github.com/openskill/sdk-go",
        "code": '''package main

import "github.com/openskill/sdk-go"

func main() {
    client := openskill.New("YOUR_API_KEY")
    apps, _ := client.Apps.List()
    fmt.Println(apps)
}''',
    },
    "curl": {
        "install": "",
        "code": '''curl -X GET "https://api.openskill.io/api/v1/apps" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json"''',
    },
}


def get_quickstart(language: str) -> dict:
    tmpl = TEMPLATES.get(language)
    if not tmpl:
        return {"error": f"Unsupported language: {language}", "available": list(TEMPLATES.keys())}
    return {"language": language, "install": tmpl["install"], "code": tmpl["code"],
            "has_install": bool(tmpl["install"])}


def list_languages() -> list[dict]:
    return [{"language": k, "has_install": bool(v["install"])} for k, v in TEMPLATES.items()]
