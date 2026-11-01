"""Developer knowledge base — searchable FAQ and guides for developer support."""


KNOWLEDGE_BASE = [
    {"id": "kb-001", "title": "Getting Started", "category": "basics", "content": "Create your developer account, set up your first app, and submit for review.", "tags": ["setup", "onboarding"]},
    {"id": "kb-002", "title": "OAuth Integration", "category": "auth", "content": "Implement OAuth 2.0 PKCE flow for secure authentication.", "tags": ["oauth", "security", "pkce"]},
    {"id": "kb-003", "title": "Webhook Best Practices", "category": "webhooks", "content": "Implement idempotency, retry logic, and signature verification.", "tags": ["webhooks", "reliability"]},
    {"id": "kb-004", "title": "Sandbox Testing", "category": "testing", "content": "Use the sandbox environment to test your app before publishing.", "tags": ["sandbox", "testing"]},
    {"id": "kb-005", "title": "Rate Limits", "category": "api", "content": "API rate limits, quotas, and how to handle 429 responses.", "tags": ["rate-limit", "api", "429"]},
    {"id": "kb-006", "title": "Publishing Guidelines", "category": "marketplace", "content": "Requirements for listing your app on the marketplace.", "tags": ["publish", "review"]},
]


def search_knowledge_base(*, query: str) -> list[dict]:
    q = query.lower()
    results = []
    for article in KNOWLEDGE_BASE:
        score = 0
        if q in article["title"].lower():
            score += 10
        if q in article["content"].lower():
            score += 5
        if any(q in tag for tag in article["tags"]):
            score += 8
        if score > 0:
            results.append({**article, "_score": score})
    return sorted(results, key=lambda r: -r["_score"])


def get_articles_by_category(*, category: str) -> list[dict]:
    return [a for a in KNOWLEDGE_BASE if a["category"] == category]


def get_popular_articles(*, view_counts: dict[str, int], limit: int = 5) -> list[dict]:
    scored = [(a, view_counts.get(a["id"], 0)) for a in KNOWLEDGE_BASE]
    scored.sort(key=lambda x: -x[1])
    return [a for a, _ in scored[:limit]]
