"use client";
export function FleetAiCostAllocPanel({ allocators, active, teams, totalUsd, allocatedPct }: { allocators: number; active: number; teams: number; totalUsd: number; allocatedPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Cost Allocation</h3>
    <div className="text-sm">{active}/{allocators} active · {teams} teams · ${totalUsd.toLocaleString()} · {allocatedPct}% allocated</div>
  </div>);
}
