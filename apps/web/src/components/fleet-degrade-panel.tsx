"use client";
export function FleetDegradePanel({ total, degraded, withFallback, withoutFallback, allProtected }: { total: number; degraded: number; withFallback: number; withoutFallback: number; allProtected: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📉 Graceful Degradation</h3>
    <div className="text-sm">{withFallback}/{total} with fallback · {degraded} currently degraded</div>
    {!allProtected && <span className="text-xs text-yellow-600">⚠️ {withoutFallback} without fallback</span>}
  </div>);
}
