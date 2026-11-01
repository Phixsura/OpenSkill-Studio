"use client";
export function FleetDnsHealthPanel({ total, healthy, failed, slow, allOk }: { total: number; healthy: number; failed: number; slow: number; allOk: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 DNS Health</h3>
    {allOk ? <span className="text-xs text-green-600">✅ All {total} resolving fast</span>
     : <span className="text-xs text-yellow-600">⚠️ {failed} failed · {slow} slow of {total}</span>}
  </div>);
}
