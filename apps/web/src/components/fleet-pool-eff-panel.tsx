"use client";
export function FleetPoolEffPanel({ active, idle, efficiencyPct, wasteful }: { active: number; idle: number; efficiencyPct: number; wasteful: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔌 Pool Efficiency</h3>
    <div className="text-sm">{active} active · {idle} idle · {efficiencyPct}%</div>
    {wasteful && <span className="text-xs text-yellow-600">💸 Low pool utilization</span>}
  </div>);
}
