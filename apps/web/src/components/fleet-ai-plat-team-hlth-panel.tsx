"use client";
export function FleetAiPlatTeamHlthPanel({ trackers, active, teams, happiness, burnout }: { trackers: number; active: number; teams: number; happiness: number; burnout: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👥 AI Team Health</h3>
    <div className="text-sm">{active}/{trackers} active · {teams} teams · {happiness}% happiness · {burnout}% burnout risk</div>
  </div>);
}
