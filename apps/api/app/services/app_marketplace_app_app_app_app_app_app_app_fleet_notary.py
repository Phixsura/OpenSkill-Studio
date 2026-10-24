"""Fleet Notary — track container image trust and signing."""
from __future__ import annotations
def fleet_notary_status(images: list[dict]) -> dict:
    signed = [i for i in images if i.get("notary_signed", False)]
    trusted = [i for i in images if i.get("trust_verified", False)]
    return {"total": len(images), "signed": len(signed), "trusted": len(trusted),
            "unsigned": len(images) - len(signed), "fully_trusted": len(trusted) == len(images)}
