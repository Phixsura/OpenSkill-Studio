"""App pricing v2 — dynamic pricing with usage-based and tiered models."""


def create_pricing_model(*, model_type: str, tiers: list[dict] | None = None,
                            per_unit_price_cents: int | None = None, unit_name: str = "API call") -> dict:
    valid_models = {"free", "flat", "tiered", "usage_based", "freemium"}
    if model_type not in valid_models:
        return {"error": f"Invalid model. Use: {', '.join(sorted(valid_models))}"}
    return {"model_type": model_type, "tiers": tiers or [], "per_unit_price_cents": per_unit_price_cents,
            "unit_name": unit_name, "error": None}


def calculate_price(*, model: dict, usage: int) -> dict:
    if model["model_type"] == "free":
        return {"total_cents": 0, "breakdown": []}
    if model["model_type"] == "flat":
        price = model["tiers"][0]["price_cents"] if model["tiers"] else 0
        return {"total_cents": price, "breakdown": [{"tier": "flat", "amount": price}]}
    if model["model_type"] == "usage_based":
        total = usage * (model.get("per_unit_price_cents", 0))
        return {"total_cents": total, "breakdown": [{"units": usage, "rate": model["per_unit_price_cents"], "amount": total}]}
    if model["model_type"] == "tiered":
        total = 0
        breakdown = []
        remaining = usage
        for tier in model.get("tiers", []):
            tier_limit = tier.get("up_to", float("inf"))
            in_tier = min(remaining, tier_limit)
            cost = in_tier * tier.get("per_unit_cents", 0)
            breakdown.append({"tier": tier.get("name", ""), "units": in_tier, "cost": cost})
            total += cost
            remaining -= in_tier
            if remaining <= 0:
                break
        return {"total_cents": total, "breakdown": breakdown}
    return {"total_cents": 0, "breakdown": []}
