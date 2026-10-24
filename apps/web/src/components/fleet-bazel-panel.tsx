"use client";
export function FleetBazelPanel({ totalBuilds, avgCacheHit, avgBuild, remoteExec, fast }: { totalBuilds: number; avgCacheHit: number; avgBuild: number; remoteExec: number; fast: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔨 Bazel</h3>
    <div className="text-sm">{avgCacheHit}% cache · {avgBuild}s avg · {remoteExec} remote</div>
    {fast && <span className="text-xs text-green-600">⚡ Fast builds</span>}
  </div>);
}
