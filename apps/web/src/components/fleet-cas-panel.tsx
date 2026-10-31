"use client";
export function FleetCasPanel({ totalEvents, scaleUps, scaleDowns, failed, healthy }: { totalEvents: number; scaleUps: number; scaleDowns: number; failed: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚙️ Cluster Autoscaler</h3>
    <div className="text-sm">⬆️ {scaleUps} · ⬇️ {scaleDowns} · ❌ {failed}</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {failed} failed scaling events</span>}
  </div>);
}
