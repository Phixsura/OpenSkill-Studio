"use client";
export function FleetEpSlaPanel({ total, meetingSla, violating, compliancePct }: { total: number; meetingSla: number; violating: number; compliancePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 Endpoint SLA</h3>
    <div className={`text-lg font-bold ${compliancePct >= 95 ? "text-green-600" : "text-red-500"}`}>{compliancePct}%</div>
    <div className="text-xs text-gray-400">{meetingSla} meeting · {violating} violating of {total}</div>
  </div>);
}
