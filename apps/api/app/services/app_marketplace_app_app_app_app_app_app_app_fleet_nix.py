"""Fleet Nix — track reproducible build environment adoption."""
from __future__ import annotations
def fleet_nix_status(repos: list[dict]) -> dict:
    using_nix = [r for r in repos if r.get("uses_nix", False)]
    reproducible = [r for r in using_nix if r.get("reproducible", False)]
    return {"total": len(repos), "using_nix": len(using_nix), "reproducible": len(reproducible),
            "adoption_pct": round(len(using_nix) / max(len(repos), 1) * 100, 1)}
