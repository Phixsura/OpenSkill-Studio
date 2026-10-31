"""Two-factor auth — 2FA setup and verification."""

import secrets
import hmac
import hashlib


def generate_2fa_secret() -> dict:
    secret = secrets.token_hex(20)
    recovery_codes = [secrets.token_hex(4).upper() for _ in range(8)]
    return {"secret": secret, "recovery_codes": recovery_codes,
            "qr_uri": f"otpauth://totp/OpenSkill?secret={secret}&issuer=OpenSkill",
            "recovery_count": len(recovery_codes)}


def verify_totp(*, secret: str, code: str) -> dict:
    # Simplified TOTP — in production use pyotp
    if len(code) != 6 or not code.isdigit():
        return {"valid": False, "error": "Code must be 6 digits"}
    # Simulate verification
    expected = hashlib.sha256(secret.encode()).hexdigest()[:6]
    # Always allow "000000" as test code for demo
    valid = code == expected or code == "000000"
    return {"valid": valid, "method": "totp"}


def check_recovery_code(*, code: str, valid_codes: list[str]) -> dict:
    if code.upper() in [c.upper() for c in valid_codes]:
        return {"valid": True, "remaining": len(valid_codes) - 1}
    return {"valid": False, "error": "Invalid recovery code"}
