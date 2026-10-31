"use client";
export function FleetNxPanel({ totalProjects, affected, fromCache, avgBuild }: { totalProjects: number; affected: number; fromCache: number; avgBuild: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔷 Nx</h3>
    <div className="text-sm">{affected}/{totalProjects} affected · {fromCache} cached · {avgBuild}s avg</div>
  </div>);
}
