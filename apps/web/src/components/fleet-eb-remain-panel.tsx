"use client";
const SC: Record<string, string> = { safe: "text-green-600", warning: "text-yellow-600", critical: "text-red-500" };
export function FleetEbRemainPanel({ remainingMin, remainingPct, status }: { remainingMin: number; remainingPct: number; status: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 Error Budget</h3>
    <div className={`text-lg font-bold ${SC[status] ?? ""}`}>{remainingPct}% remaining</div>
    <div className="text-xs text-gray-400">{remainingMin}min left</div>
  </div>);
}
