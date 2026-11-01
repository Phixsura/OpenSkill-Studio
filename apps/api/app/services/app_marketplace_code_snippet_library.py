"""Code snippet library — curated code examples for SDK integration."""

import html


SNIPPETS = {
    "install_app": {
        "title": "Install an App",
        "languages": {
            "typescript": 'import { OpenSkill } from "@openskill/sdk";\n\nconst sdk = new OpenSkill({ apiKey: "sk_..." });\nawait sdk.apps.install("app_id");',
            "python": 'from openskill import OpenSkill\n\nsdk = OpenSkill(api_key="sk_...")\nsdk.apps.install("app_id")',
            "curl": 'curl -X POST https://api.openskill.dev/v1/apps/app_id/install \\\n  -H "Authorization: Bearer sk_..."',
        },
        "category": "getting_started",
    },
    "webhook_verify": {
        "title": "Verify Webhook Signature",
        "languages": {
            "typescript": 'import { verifySignature } from "@openskill/sdk";\n\nconst valid = verifySignature(payload, signature, secret);',
            "python": 'from openskill import verify_signature\n\nvalid = verify_signature(payload, signature, secret)',
        },
        "category": "webhooks",
    },
}


def list_snippets(*, category: str | None = None, language: str | None = None) -> dict:
    results = []
    for sid, snip in SNIPPETS.items():
        if category and snip["category"] != category:
            continue
        langs = list(snip["languages"].keys())
        if language and language not in langs:
            continue
        results.append({"id": sid, "title": snip["title"],
                         "category": snip["category"], "languages": langs})
    categories = sorted(set(s["category"] for s in SNIPPETS.values()))
    return {"snippets": results, "total": len(results), "categories": categories}


def get_snippet(*, snippet_id: str, language: str) -> dict:
    snip = SNIPPETS.get(snippet_id)
    if not snip:
        return {"error": f"Snippet not found: {snippet_id}"}
    code = snip["languages"].get(language)
    if not code:
        return {"error": f"Language not available: {language}"}
    return {"id": snippet_id, "title": snip["title"], "language": language,
            "code": code, "html_safe_code": html.escape(code)}
