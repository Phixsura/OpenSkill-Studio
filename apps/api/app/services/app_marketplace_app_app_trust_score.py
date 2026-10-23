"""App trust score — composite trust metric for marketplace apps."""


def calculate_trust_score(*, signals: dict) -> dict:
    weights = {
        "verified_developer": 20,
        "security_scan_clean": 20,
        "code_signed": 15,
        "privacy_policy": 10,
        "responsive_support": 10,
        "high_rating": 10,
        "active_maintenance": 10,
        "open_source": 5,
    }
    earned = 0
    details = []
    for signal, weight in weights.items():
        met = signals.get(signal, False)
        if met:
            earned += weight
        details.append({"signal": signal, "weight": weight, "met": met})
    trust_level = "high" if earned >= 80 else "medium" if earned >= 50 else "low"
    return {
        "score": earned,
        "max_score": 100,
        "trust_level": trust_level,
        "details": details,
        "met_count": sum(1 for d in details if d["met"]),
        "total_signals": len(details),
        "badge": "🛡️ Trusted" if earned >= 80 else "⚠️ Review" if earned < 50 else "",
    }
