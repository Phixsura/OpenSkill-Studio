"use client";
export function FleetDrPanel({ total, passed, failed, lastDrillDays, ready }: { total: number; passed: number; failed: number; lastDrillDays: number; ready: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏥 DR Readiness</h3>
    <div className="text-sm">{passed}/{total} checks · Last drill {lastDrillDays}d ago</div>
    <span className={`text-xs ${ready ? "text-green-600" : "text-red-500"}`}>{ready ? "✅ Ready" : "❌ Not ready"}</span>
  </div>);
}
