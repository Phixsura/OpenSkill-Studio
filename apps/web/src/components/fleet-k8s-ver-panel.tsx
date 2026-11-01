"use client";
export function FleetK8sVerPanel({ total, versionCount, skewed }: { total: number; versionCount: number; skewed: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ K8s Versions</h3>
    <div className="text-sm">{total} nodes · {versionCount} versions</div>
    {skewed && <span className="text-xs text-yellow-600">⚠️ Version skew detected</span>}
  </div>);
}
