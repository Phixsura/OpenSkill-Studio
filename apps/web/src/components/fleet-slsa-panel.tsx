"use client";
export function FleetSlsaPanel({ total, avgLevel, mature }: { total: number; avgLevel: number; mature: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 SLSA</h3>
    <div className={`text-lg font-bold ${mature ? "text-green-600" : "text-yellow-600"}`}>Level {avgLevel} avg</div>
    <div className="text-xs text-gray-400">{total} builds assessed</div>
  </div>);
}
