"use client";
export function FleetLbHealthPanel({ lbs, healthyBackends, totalBackends, healthPct, ok }: { lbs: number; healthyBackends: number; totalBackends: number; healthPct: number; ok: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ Load Balancers</h3>
    <div className="text-sm">{healthyBackends}/{totalBackends} backends healthy ({healthPct}%)</div>
    <span className={`text-xs ${ok ? "text-green-600" : "text-red-500"}`}>{ok ? "✅" : "⚠️"} {lbs} LBs</span>
  </div>);
}
