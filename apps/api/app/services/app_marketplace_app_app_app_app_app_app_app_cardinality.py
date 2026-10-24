"""Metric cardinality analyzer — detect high-cardinality metric issues."""
from __future__ import annotations


def analyze_cardinality(metrics: list[dict]) -> dict:
    high_card = []
    total_series = 0
    for m in metrics:
        series = m.get("series_count", 0)
        total_series += series
        if series > 10000:
            high_card.append({"metric": m["name"], "series": series,
                               "labels": m.get("label_count", 0),
                               "recommendation": "Reduce label cardinality"})
    return {"total_metrics": len(metrics), "total_series": total_series,
            "high_cardinality": high_card, "high_card_count": len(high_card),
            "estimated_cost_factor": round(total_series / 10000, 1)}


def label_analysis(metric: dict) -> dict:
    labels = metric.get("labels", {})
    results = []
    for label, values in labels.items():
        results.append({"label": label, "unique_values": values,
                         "high_cardinality": values > 1000})
    return {"metric": metric["name"], "labels": results,
            "total_labels": len(results),
            "high_card_labels": sum(1 for r in results if r["high_cardinality"])}
