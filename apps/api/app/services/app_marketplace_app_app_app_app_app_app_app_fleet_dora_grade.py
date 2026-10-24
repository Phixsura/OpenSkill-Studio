"""Fleet DORA overall grade — composite DORA performance level."""
from __future__ import annotations
def fleet_dora_overall(df_level: str, lt_level: str, cfr_level: str, mttr_level: str) -> dict:
    scores = {"Elite": 4, "High": 3, "Medium": 2, "Low": 1}
    avg = (scores.get(df_level, 1) + scores.get(lt_level, 1) + scores.get(cfr_level, 1) + scores.get(mttr_level, 1)) / 4
    if avg >= 3.5: grade = "Elite"
    elif avg >= 2.5: grade = "High"
    elif avg >= 1.5: grade = "Medium"
    else: grade = "Low"
    return {"df": df_level, "lt": lt_level, "cfr": cfr_level, "mttr": mttr_level,
            "overall": grade, "score": round(avg, 2)}
