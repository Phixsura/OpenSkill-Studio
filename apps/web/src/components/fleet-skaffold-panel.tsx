"use client";
export function FleetSkaffoldPanel({ totalDevs, activeLoops, avgSync, fast }: { totalDevs: number; activeLoops: number; avgSync: number; fast: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Skaffold</h3>
    <div className="text-sm">{activeLoops}/{totalDevs} dev loops · avg {avgSync}ms sync</div>
    {fast && <span className="text-xs text-green-600">⚡ Fast inner loop</span>}
  </div>);
}
