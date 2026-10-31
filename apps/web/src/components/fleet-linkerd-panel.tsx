"use client";
export function FleetLinkerdPanel({ total, meshed, unmeshed, avgSuccessRate, healthy }: { total: number; meshed: number; unmeshed: number; avgSuccessRate: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 Linkerd</h3>
    <div className="text-sm">{meshed}/{total} meshed · {avgSuccessRate}% success</div>
    {!healthy && <span className="text-xs text-yellow-600">⚠️ Below 99% success rate</span>}
  </div>);
}
