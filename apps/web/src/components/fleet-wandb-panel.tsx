"use client";
export function FleetWandbPanel({ projects, active, runs, artifacts }: { projects: number; active: number; runs: number; artifacts: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 W&B</h3>
    <div className="text-sm">{active}/{projects} active · {runs.toLocaleString()} runs · {artifacts} artifacts</div>
  </div>);
}
