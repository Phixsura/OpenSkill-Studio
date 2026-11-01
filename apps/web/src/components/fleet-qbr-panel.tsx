"use client";
export function FleetQbrPanel({ quarter, target, actual, achievementPct, targetHit }: { quarter: string; target: number; actual: number; achievementPct: number; targetHit: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 {quarter} Review</h3>
    <div className={`text-lg font-bold ${targetHit ? "text-green-600" : "text-red-500"}`}>{achievementPct}%</div>
    <div className="text-xs text-gray-400">${actual.toLocaleString()} / ${target.toLocaleString()}</div>
  </div>);
}
