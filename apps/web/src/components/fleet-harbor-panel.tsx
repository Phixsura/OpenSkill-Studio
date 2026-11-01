"use client";
export function FleetHarborPanel({ projects, repos, artifacts, overQuota, healthy }: { projects: number; repos: number; artifacts: number; overQuota: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚓ Harbor</h3>
    <div className="text-sm">{projects} projects · {repos} repos · {artifacts.toLocaleString()} artifacts</div>
    {!healthy && <span className="text-xs text-yellow-600">⚠️ {overQuota} over quota</span>}
  </div>);
}
