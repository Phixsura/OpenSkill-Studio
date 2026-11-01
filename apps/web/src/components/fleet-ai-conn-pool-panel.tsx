"use client";
export function FleetAiConnPoolPanel({ pools, active, max, activeConns, utilization }: { pools: number; active: number; max: number; activeConns: number; utilization: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔌 AI Connection Pool</h3>
    <div className="text-sm">{active}/{pools} active · {activeConns}/{max} conns · {utilization}% util</div>
  </div>);
}
