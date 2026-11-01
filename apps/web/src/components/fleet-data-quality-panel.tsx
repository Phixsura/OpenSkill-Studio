"use client";
export function FleetDataQualityPanel({ total, good, poor, avgScore, highQuality }: { total: number; good: number; poor: number; avgScore: number; highQuality: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Data Quality</h3>
    <div className={`text-lg font-bold ${highQuality ? "text-green-600" : "text-yellow-600"}`}>{avgScore}/100</div>
    <div className="text-xs text-gray-400">{good} good · {poor} poor of {total}</div>
  </div>);
}
