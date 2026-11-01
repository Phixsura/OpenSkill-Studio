"use client";
export function FleetAiCollabHubPanel({ hubs, active, teams, sharedModels, discussions }: { hubs: number; active: number; teams: number; sharedModels: number; discussions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤝 AI Collaboration Hub</h3>
    <div className="text-sm">{active}/{hubs} active · {teams} teams · {sharedModels} shared · {discussions.toLocaleString()} discussions</div>
  </div>);
}
