"""Developer docs index — structured documentation tree."""

DOCS_TREE = [
    {"section": "Getting Started", "pages": [
        {"slug": "quickstart", "title": "Quick Start Guide"},
        {"slug": "first-app", "title": "Build Your First App"},
    ]},
    {"section": "API Reference", "pages": [
        {"slug": "authentication", "title": "Authentication"},
        {"slug": "apps", "title": "Apps API"},
        {"slug": "webhooks", "title": "Webhooks"},
        {"slug": "sandbox", "title": "Sandbox Execution"},
    ]},
    {"section": "SDKs", "pages": [
        {"slug": "typescript-sdk", "title": "TypeScript SDK"},
        {"slug": "python-sdk", "title": "Python SDK"},
        {"slug": "extension-sdk", "title": "Extension SDK"},
    ]},
]


def get_docs_tree() -> list[dict]:
    return DOCS_TREE


def search_docs(query: str) -> list[dict]:
    q = query.lower()
    results = []
    for section in DOCS_TREE:
        for page in section["pages"]:
            if q in page["title"].lower() or q in page["slug"]:
                results.append({**page, "section": section["section"]})
    return results
