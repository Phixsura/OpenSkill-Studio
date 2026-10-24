"use client";
export function FleetHexPanel({ workspaces, active, projects, runs }: { workspaces: number; active: number; projects: number; runs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔷 Hex</h3>
    <div className="text-sm">{active}/{workspaces} active · {projects} projects · {runs.toLocaleString()} runs</div>
  </div>);
}
