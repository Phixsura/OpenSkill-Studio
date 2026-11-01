"use client";
export function FleetAiCostAttrPanel({ teams, totalMonthly, topSpender }: { teams: number; totalMonthly: number; topSpender: string | null; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Cost Attribution</h3>
    <div className="text-sm">{teams} teams · ${totalMonthly.toLocaleString()}/mo</div>
    {topSpender && <div className="text-xs text-blue-500">Top: {topSpender}</div>}
  </div>);
}
