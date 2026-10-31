"use client";
export function FleetValueStreamPanel({ stages, totalCycle, efficiencyPct, bottleneck }: { stages: number; totalCycle: number; efficiencyPct: number; bottleneck: string | null; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Value Stream</h3>
    <div className="text-sm">{stages} stages · {totalCycle}h cycle · {efficiencyPct}% efficient</div>
    {bottleneck && <div className="text-xs text-yellow-600">⚠️ Bottleneck: {bottleneck}</div>}
  </div>);
}
