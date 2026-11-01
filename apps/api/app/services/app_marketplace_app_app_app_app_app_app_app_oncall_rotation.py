"""On-call rotation manager — manage on-call schedules and escalation."""
from __future__ import annotations


class OnCallRotation:
    def __init__(self):
        self._rotations: dict[str, dict] = {}

    def create(self, team: str, members: list[str], rotation_days: int = 7) -> dict:
        self._rotations[team] = {"team": team, "members": members,
                                  "rotation_days": rotation_days, "current_idx": 0}
        return {"team": team, "members": len(members), "rotation_days": rotation_days}

    def current_oncall(self, team: str, day_number: int = 0) -> dict:
        rot = self._rotations[team]
        idx = (day_number // rot["rotation_days"]) % len(rot["members"])
        primary = rot["members"][idx]
        secondary = rot["members"][(idx + 1) % len(rot["members"])]
        return {"team": team, "primary": primary, "secondary": secondary,
                "rotation_day": day_number % rot["rotation_days"] + 1}

    def escalation_chain(self, team: str, day_number: int = 0) -> list[str]:
        rot = self._rotations[team]
        idx = (day_number // rot["rotation_days"]) % len(rot["members"])
        chain = []
        for i in range(len(rot["members"])):
            chain.append(rot["members"][(idx + i) % len(rot["members"])])
        return chain

    def list_teams(self) -> list[dict]:
        return [{"team": t, "members": len(r["members"]), "rotation_days": r["rotation_days"]}
                for t, r in self._rotations.items()]
