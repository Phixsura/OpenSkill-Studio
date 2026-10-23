"""Developer referral — invite other developers and earn rewards."""

import hashlib
import secrets


def generate_referral_code(*, developer_id: str) -> str:
    return f"ref_{hashlib.sha256(f'{developer_id}:{secrets.token_hex(8)}'.encode()).hexdigest()[:8]}"


def create_referral(*, referrer_id: str, code: str) -> dict:
    return {"referrer_id": referrer_id, "code": code, "signups": 0,
            "conversions": 0, "total_reward_cents": 0, "status": "active"}


def process_referral_signup(*, referral: dict) -> dict:
    signups = referral["signups"] + 1
    reward = 500 if signups <= 10 else 250  # $5 first 10, $2.50 after
    return {**referral, "signups": signups, "total_reward_cents": referral["total_reward_cents"] + reward}


def get_referral_stats(*, referrals: list[dict]) -> dict:
    total_signups = sum(r.get("signups", 0) for r in referrals)
    total_rewards = sum(r.get("total_reward_cents", 0) for r in referrals)
    return {"total_referrals": len(referrals), "total_signups": total_signups,
            "total_rewards": f"${total_rewards / 100:,.2f}",
            "avg_signups": round(total_signups / max(len(referrals), 1), 1)}
