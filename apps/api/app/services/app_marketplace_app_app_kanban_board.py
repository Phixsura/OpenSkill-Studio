"""Kanban board — task columns with drag support."""

import html
from datetime import datetime, timezone


def build_kanban_board(*, columns: list[dict]) -> dict:
    board = []
    total_cards = 0
    for col in columns:
        cards = []
        for card in col.get("cards", []):
            cards.append({
                "id": card["id"],
                "title": html.escape(card.get("title", "")),
                "assignee": html.escape(card.get("assignee", "")),
                "priority": card.get("priority", "medium"),
                "labels": card.get("labels", []),
            })
        total_cards += len(cards)
        board.append({"id": col["id"], "title": html.escape(col.get("title", "")),
                       "cards": cards, "card_count": len(cards),
                       "wip_limit": col.get("wip_limit"),
                       "over_limit": col.get("wip_limit") is not None and len(cards) > col["wip_limit"]})
    return {"columns": board, "total_cards": total_cards,
            "updated_at": datetime.now(timezone.utc).isoformat()}
