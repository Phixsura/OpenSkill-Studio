"use client";
export function FleetXpCompPanel({ total, ready, notReady, managedResources }: { total: number; ready: number; notReady: number; managedResources: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ Crossplane XRs</h3>
    <div className="text-sm">{ready}/{total} ready · {managedResources} managed</div>
    {notReady > 0 && <span className="text-xs text-yellow-600">⚠️ {notReady} not ready</span>}
  </div>);
}
