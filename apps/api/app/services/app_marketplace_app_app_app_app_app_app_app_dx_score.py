"""Developer experience score — measure overall DX quality."""
from __future__ import annotations


def compute_dx_score(*, docs_coverage: float, sdk_languages: int,
                       avg_onboarding_min: float, api_uptime: float,
                       support_response_hours: float, sandbox_available: bool,
                       cli_available: bool, changelog_frequency: str) -> dict:
    score = 0
    # Docs (0-20)
    score += min(20, int(docs_coverage * 20))
    # SDKs (0-15)
    score += min(15, sdk_languages * 3)
    # Onboarding (0-15)
    score += max(0, 15 - int(avg_onboarding_min / 2))
    # Uptime (0-15)
    score += 15 if api_uptime >= 99.9 else 10 if api_uptime >= 99 else 5
    # Support (0-10)
    score += 10 if support_response_hours < 4 else 5 if support_response_hours < 12 else 0
    # Tools (0-15)
    if sandbox_available: score += 8
    if cli_available: score += 7
    # Changelog (0-10)
    freq_scores = {"weekly": 10, "biweekly": 7, "monthly": 5, "quarterly": 2}
    score += freq_scores.get(changelog_frequency, 0)
    score = min(100, score)
    grade = "A+" if score >= 95 else "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 50 else "D"
    return {"score": score, "grade": grade, "max": 100,
            "display": f"{score}/100 ({grade})"}
