"use client";
export function FleetFailoverPanel({ regions, primary, standby, standbyReady, failoverReady }: { regions: number; primary: number; standby: number; standbyReady: number; failoverReady: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Failover</h3>
    <div className="text-sm">{primary} primary · {standby} standby ({standbyReady} ready)</div>
    <span className={`text-xs ${failoverReady ? "text-green-600" : "text-red-500"}`}>{failoverReady ? "✅ Failover ready" : "❌ No failover"}</span>
  </div>);
}
