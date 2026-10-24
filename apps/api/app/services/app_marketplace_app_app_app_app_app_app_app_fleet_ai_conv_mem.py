"""Fleet AI Conversation Memory — track persistent dialogue state."""
from __future__ import annotations
def fleet_ai_conv_memory(stores: list[dict]) -> dict:
    active = [s for s in stores if s.get("active", True)]
    conversations = sum(s.get("conversations", 0) for s in stores)
    messages_stored = sum(s.get("messages", 0) for s in stores)
    return {"stores": len(stores), "active": len(active), "conversations": conversations,
            "messages": messages_stored, "all_active": len(active) == len(stores)}
