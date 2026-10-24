"""Fleet AI Conversation Memory — track long-term AI conversation state."""
from __future__ import annotations
def fleet_ai_conversation_memory(stores: list[dict]) -> dict:
    active = [s for s in stores if s.get("active", True)]
    conversations = sum(s.get("conversations", 0) for s in stores)
    messages_stored = sum(s.get("messages", 0) for s in stores)
    avg_context_len = round(sum(s.get("avg_context", 0) for s in stores) / max(len(stores), 1))
    return {"stores": len(stores), "active": len(active), "conversations": conversations,
            "messages": messages_stored, "avg_context": avg_context_len, "deep": avg_context_len > 10000}
