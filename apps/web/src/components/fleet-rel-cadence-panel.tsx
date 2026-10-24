"use client";
export function FleetRelCadencePanel({ total, avgGapDays, regular }: { total: number; avgGapDays: number; regular: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📅 Release Cadence</h3>
    <div className="text-sm">{total} releases · every {avgGapDays} days</div>
    <span className={`text-xs ${regular ? "text-green-600" : "text-yellow-600"}`}>{regular ? "✅ Regular" : "⚠️ Irregular"}</span>
  </div>);
}
