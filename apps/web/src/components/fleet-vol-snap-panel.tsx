"use client";
export function FleetVolSnapPanel({ total, withSnapshot, staleSnapshots, allFresh }: { total: number; withSnapshot: number; staleSnapshots: number; allFresh: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📸 Volume Snapshots</h3>
    {allFresh ? <span className="text-xs text-green-600">✅ All {total} snapshots fresh</span>
     : <span className="text-xs text-yellow-600">⚠️ {staleSnapshots} stale snapshots</span>}
  </div>);
}
