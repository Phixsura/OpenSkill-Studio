"""Comparison table — side-by-side plan/feature comparison."""

import html


def build_comparison_table(*, plans: list[dict], features: list[dict]) -> dict:
    cols = [{"id": p["id"], "name": html.escape(p.get("name", "")),
             "price": p.get("price", "Free"), "recommended": p.get("recommended", False)}
            for p in plans]
    rows = []
    for feat in features:
        row = {"feature": html.escape(feat.get("name", "")),
               "category": feat.get("category", "General"),
               "values": {}}
        for p in plans:
            val = feat.get("values", {}).get(p["id"])
            if isinstance(val, bool):
                row["values"][p["id"]] = {"type": "bool", "value": val, "display": "✓" if val else "✗"}
            elif val is None:
                row["values"][p["id"]] = {"type": "null", "value": None, "display": "—"}
            else:
                row["values"][p["id"]] = {"type": "text", "value": val, "display": html.escape(str(val))}
        rows.append(row)
    return {"plans": cols, "features": rows, "plan_count": len(cols), "feature_count": len(rows)}
