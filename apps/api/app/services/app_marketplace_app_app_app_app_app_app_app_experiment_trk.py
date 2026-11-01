"""Experiment tracker — track and analyze platform experiments."""
from __future__ import annotations
import hashlib
import time


def create_experiment(name: str, hypothesis: str, metric: str,
                       control_value: float, target_lift: float) -> dict:
    exp_id = hashlib.sha256(f"{name}:{time.time()}".encode()).hexdigest()[:8]
    return {"id": exp_id, "name": name, "hypothesis": hypothesis,
            "metric": metric, "control_value": control_value,
            "target_lift_pct": target_lift, "status": "running",
            "started_at": time.time()}


def analyze_experiment(experiment: dict, variant_value: float) -> dict:
    control = experiment["control_value"]
    lift = round((variant_value - control) / max(abs(control), 0.01) * 100, 1)
    significant = abs(lift) >= experiment["target_lift_pct"]
    winner = "variant" if lift > 0 and significant else "control" if lift < 0 and significant else "inconclusive"
    return {"experiment": experiment["name"], "metric": experiment["metric"],
            "control": control, "variant": variant_value, "lift_pct": lift,
            "significant": significant, "winner": winner}
