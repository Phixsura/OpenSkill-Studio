"use client";
export function FleetBackupPanel({ total, fresh, stale, failed, healthy }: { total: number; fresh: number; stale: number; failed: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 Backups</h3>
    {healthy ? <span className="text-xs text-green-600">✅ All {total} fresh</span>
     : <span className="text-xs text-yellow-600">⚠️ {stale} stale · {failed} failed</span>}
  </div>);
}
