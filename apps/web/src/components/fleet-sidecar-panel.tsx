"use client";
export function FleetSidecarPanel({ total, injected, missing, coveragePct }: { total: number; injected: number; missing: number; coveragePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Sidecar Injection</h3>
    <div className="text-sm">{injected}/{total} injected ({coveragePct}%)</div>
    {missing > 0 && <span className="text-xs text-yellow-600">⚠️ {missing} without sidecar</span>}
  </div>);
}
