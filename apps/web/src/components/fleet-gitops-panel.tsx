"use client";
export function FleetGitopsPanel({ total, synced, outOfSync, allSynced }: { total: number; synced: number; outOfSync: number; allSynced: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 GitOps Sync</h3>
    {allSynced ? <span className="text-xs text-green-600">✅ All {total} synced</span>
     : <span className="text-xs text-yellow-600">⚠️ {outOfSync} out of sync</span>}
  </div>);
}
