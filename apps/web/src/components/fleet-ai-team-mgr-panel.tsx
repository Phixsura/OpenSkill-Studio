"use client";
export function FleetAiTeamMgrPanel({ managers, active, teams, members, projects }: { managers: number; active: number; teams: number; members: number; projects: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👥 AI Team Manager</h3>
    <div className="text-sm">{active}/{managers} active · {teams} teams · {members} members · {projects} projects</div>
  </div>);
}
