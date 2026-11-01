"use client";
export function FleetVeleroPanel({ total, completed, failed, latestAge, fresh }: { total: number; completed: number; failed: number; latestAge: number; fresh: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 Velero Backups</h3>
    <div className="text-sm">{completed}✅ {failed}❌ · latest {latestAge}h ago</div>
    {!fresh && <span className="text-xs text-red-500">⚠️ Stale backups!</span>}
  </div>);
}
