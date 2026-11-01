"use client";
export function FleetFeatureFlagsPanel({ total, enabled, stale, needsCleanup }: { total: number; enabled: number; stale: number; needsCleanup: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚩 Feature Flags</h3>
    <div className="text-sm">{enabled}/{total} enabled</div>
    {needsCleanup && <span className="text-xs text-yellow-600">⚠️ {stale} stale flags {">"} 90 days</span>}
  </div>);
}
