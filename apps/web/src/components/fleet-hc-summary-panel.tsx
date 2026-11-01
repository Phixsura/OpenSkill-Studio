"use client";
export function FleetHcSummaryPanel({ total, passing, warning, failing, score }: { total: number; passing: number; warning: number; failing: number; score: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏥 Health Checks</h3>
    <div className={`text-lg font-bold ${score >= 90 ? "text-green-600" : score >= 70 ? "text-yellow-600" : "text-red-500"}`}>{score}%</div>
    <div className="text-xs text-gray-400">{passing}✅ {warning}⚠️ {failing}❌ of {total}</div>
  </div>);
}
