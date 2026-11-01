"use client";
export function FleetToilPanel({ toilHours, engHours, toilPct, acceptable }: { toilHours: number; engHours: number; toilPct: number; acceptable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 Toil Budget</h3>
    <div className={`text-lg font-bold ${acceptable ? "text-green-600" : "text-red-500"}`}>{toilPct}% toil</div>
    <div className="text-xs text-gray-400">{toilHours}h toil · {engHours}h engineering</div>
  </div>);
}
