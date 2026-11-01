"use client";
export function FleetOctantPanel({ totalSessions, active, clustersViewed }: { totalSessions: number; active: number; clustersViewed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔭 Octant</h3>
    <div className="text-sm">{active}/{totalSessions} active · {clustersViewed} clusters viewed</div>
  </div>);
}
