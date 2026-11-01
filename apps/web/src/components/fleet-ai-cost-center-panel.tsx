"use client";
export function FleetAiCostCenterPanel({ centers, active, teams, total, allocated }: { centers: number; active: number; teams: number; total: number; allocated: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Cost Center</h3>
    <div className="text-sm">{active}/{centers} active · {teams} teams · ${total.toLocaleString()} · {allocated}% allocated</div>
  </div>);
}
