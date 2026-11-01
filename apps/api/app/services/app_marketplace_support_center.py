"""Support center — self-service support with FAQ, troubleshooting, and contact."""

FAQ_ITEMS = [
    {"id": "faq-1", "question": "How do I publish an app?", "answer": "Submit your app for review after completing the manifest and uploading a version.", "category": "publishing"},
    {"id": "faq-2", "question": "How are apps reviewed?", "answer": "Our review team checks security, performance, and compliance within 2-3 business days.", "category": "publishing"},
    {"id": "faq-3", "question": "What are webhooks?", "answer": "Webhooks are HTTP callbacks that notify your server when events occur.", "category": "technical"},
    {"id": "faq-4", "question": "How do I rotate API keys?", "answer": "Go to Settings > API Keys and click Rotate. Old keys have a 24h grace period.", "category": "security"},
    {"id": "faq-5", "question": "What are rate limits?", "answer": "Free: 1K/min, Starter: 10K/min, Pro: 100K/min. Contact us for enterprise.", "category": "billing"},
]


def search_faq(*, query: str) -> list[dict]:
    q = query.lower()
    results = []
    for item in FAQ_ITEMS:
        score = 0
        if q in item["question"].lower():
            score += 10
        if q in item["answer"].lower():
            score += 5
        if score > 0:
            results.append({**item, "_score": score})
    return sorted(results, key=lambda r: -r["_score"])


def get_faq_by_category(*, category: str) -> list[dict]:
    return [f for f in FAQ_ITEMS if f["category"] == category]


def create_support_ticket(*, user_id: str, subject: str, description: str,
                             category: str, priority: str = "normal") -> dict:
    valid_priorities = {"low", "normal", "high", "urgent"}
    if priority not in valid_priorities:
        return {"error": f"Invalid priority: {priority}"}
    return {"user_id": user_id, "subject": subject, "description": description,
            "category": category, "priority": priority, "status": "open", "error": None}


def build_troubleshooting_guide(*, symptom: str) -> list[dict]:
    guides = {
        "webhook_not_delivered": [
            {"step": 1, "action": "Check endpoint URL is correct and reachable"},
            {"step": 2, "action": "Verify webhook secret matches"},
            {"step": 3, "action": "Check for 429 rate limit responses"},
            {"step": 4, "action": "Review webhook delivery logs"},
        ],
        "api_errors": [
            {"step": 1, "action": "Check API key is valid and not expired"},
            {"step": 2, "action": "Verify request format matches API spec"},
            {"step": 3, "action": "Check rate limit usage"},
        ],
    }
    return guides.get(symptom, [{"step": 1, "action": "Contact support for help"}])
