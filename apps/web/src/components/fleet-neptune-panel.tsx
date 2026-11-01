"use client";
export function FleetNeptunePanel({ projects, active, runs, storageGb }: { projects: number; active: number; runs: number; storageGb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔱 Neptune</h3>
    <div className="text-sm">{active}/{projects} active · {runs.toLocaleString()} runs · {storageGb}GB</div>
  </div>);
}
