"""Developer FAQ — searchable frequently asked questions."""
from __future__ import annotations
import html

FAQS = [
    {"id": "q1", "question": "How do I get an API key?", "answer": "Go to Settings > API Keys and click 'Generate Key'.", "category": "getting-started"},
    {"id": "q2", "question": "What are the rate limits?", "answer": "Free plan: 1,000/min. Pro: 10,000/min. Enterprise: custom.", "category": "api"},
    {"id": "q3", "question": "How do webhooks work?", "answer": "We send POST requests to your endpoint when events occur.", "category": "webhooks"},
    {"id": "q4", "question": "How do I deploy my app?", "answer": "Use the Deploy button or CI/CD pipeline with our GitHub Action.", "category": "deploy"},
    {"id": "q5", "question": "Can I use custom domains?", "answer": "Yes, on Pro and Enterprise plans. Add a CNAME record.", "category": "features"},
    {"id": "q6", "question": "How is billing calculated?", "answer": "Usage-based billing with tiered pricing. See Billing page.", "category": "billing"},
]


def search_faq(query: str) -> list[dict]:
    q = query.lower()
    return [{"id": f["id"], "question": f["question"], "answer": f["answer"],
             "category": f["category"]}
            for f in FAQS if q in f["question"].lower() or q in f["answer"].lower()]


def get_by_category(category: str) -> list[dict]:
    return [f for f in FAQS if f["category"] == category]


def list_categories() -> list[str]:
    return sorted({f["category"] for f in FAQS})
