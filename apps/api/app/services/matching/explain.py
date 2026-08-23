"""Explanation tree builder (Elasticsearch _explain style).

Invariant: parent value == sum of child values (linear scoring makes the
decomposition exact — R5/D2).
"""


def build_explain_tree(scored_item: dict, config) -> dict:
    weights: dict[str, float] = config.weights or {}
    details = []
    for name, value in scored_item["signals"].items():
        weight = weights.get(name, 0.0)
        details.append(
            {
                "value": round(weight * value, 6),
                "description": f"{name}: raw={round(value, 4)} weight={weight}",
                "details": [],
            }
        )
    return {
        "value": round(sum(d["value"] for d in details), 6),
        "description": (
            f"linear weighted sum over {len(details)} signals "
            f"(config v{config.version})"
        ),
        "details": details,
    }
