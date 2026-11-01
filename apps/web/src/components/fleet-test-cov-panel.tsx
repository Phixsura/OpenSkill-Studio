"use client";
export function FleetTestCovPanel({ coveragePct, meetsTarget, totalLines }: { coveragePct: number; meetsTarget: boolean; totalLines: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧪 Test Coverage</h3>
    <div className={`text-lg font-bold ${meetsTarget ? "text-green-600" : "text-yellow-600"}`}>{coveragePct}%</div>
    <div className="text-xs text-gray-400">{totalLines.toLocaleString()} lines · Target: 80%</div>
  </div>);
}
