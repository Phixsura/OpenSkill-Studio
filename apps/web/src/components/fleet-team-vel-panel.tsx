"use client";
export function FleetTeamVelPanel({ teams, totalPoints, avgVelocity, topTeam }: { teams: number; totalPoints: number; avgVelocity: number; topTeam: string | null; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏃 Team Velocity</h3>
    <div className="text-sm">{totalPoints} pts · avg {avgVelocity}/team · {teams} teams</div>
    {topTeam && <div className="text-xs text-blue-500">🏆 Top: {topTeam}</div>}
  </div>);
}
