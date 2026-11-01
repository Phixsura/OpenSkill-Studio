"use client";
export function FleetImgPullPanel({ total, avgPull, slowPulls, failed, healthy }: { total: number; avgPull: number; slowPulls: number; failed: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📥 Image Pulls</h3>
    <div className="text-sm">avg {avgPull}ms · {slowPulls} slow · {failed} failed</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ Pull failures detected</span>}
  </div>);
}
