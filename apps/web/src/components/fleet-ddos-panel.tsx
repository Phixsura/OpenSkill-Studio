"use client";
export function FleetDdosPanel({ zones, underAttack, mitigatedGbps, allClear }: { zones: number; underAttack: number; mitigatedGbps: number; allClear: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ DDoS Protection</h3>
    {allClear ? <span className="text-xs text-green-600">✅ All {zones} zones clear</span>
     : <span className="text-xs text-red-500">🚨 {underAttack} under attack · {mitigatedGbps} Gbps mitigated</span>}
  </div>);
}
