"use client";
export function FleetSsoPanel({ total, healthy, degraded, down, allOk }: { total: number; healthy: number; degraded: number; down: number; allOk: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 SSO Providers</h3>
    <div className="text-sm">🟢 {healthy} · 🟡 {degraded} · 🔴 {down}</div>
    {!allOk && <span className="text-xs text-yellow-600">⚠️ SSO issues detected</span>}
  </div>);
}
