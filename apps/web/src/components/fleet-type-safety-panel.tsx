"use client";
export function FleetTypeSafetyPanel({ total, strictTyped, avgCoverage, typeSafe }: { total: number; strictTyped: number; avgCoverage: number; typeSafe: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 Type Safety</h3>
    <div className={`text-lg font-bold ${typeSafe ? "text-green-600" : "text-yellow-600"}`}>{avgCoverage}%</div>
    <div className="text-xs text-gray-400">{strictTyped}/{total} strict mode</div>
  </div>);
}
