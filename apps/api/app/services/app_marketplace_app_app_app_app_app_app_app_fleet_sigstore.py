"""Fleet Sigstore — track artifact signing and verification."""
from __future__ import annotations
def fleet_sigstore_status(artifacts: list[dict]) -> dict:
    signed = [a for a in artifacts if a.get("signed", False)]
    verified = [a for a in artifacts if a.get("verified", False)]
    return {"total": len(artifacts), "signed": len(signed), "verified": len(verified),
            "unsigned": len(artifacts) - len(signed), "secure": len(signed) == len(artifacts)}
