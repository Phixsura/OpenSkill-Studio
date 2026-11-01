"""Fleet accessibility — track WCAG compliance."""
from __future__ import annotations
def fleet_accessibility(pages: list[dict]) -> dict:
    passing = [p for p in pages if p.get("wcag_aa", False)]
    aaa = [p for p in pages if p.get("wcag_aaa", False)]
    score = round(len(passing) / max(len(pages), 1) * 100, 1)
    return {"total": len(pages), "wcag_aa": len(passing), "wcag_aaa": len(aaa),
            "score": score, "compliant": score >= 95}
