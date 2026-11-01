"use client";
export function FleetSliPanel({ total, meetingTarget, missingTarget, compliancePct }: { total: number; meetingTarget: number; missingTarget: number; compliancePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Fleet SLIs</h3>
    <div className={`text-lg font-bold ${compliancePct >= 80 ? "text-green-600" : "text-red-500"}`}>{compliancePct}% compliant</div>
    <div className="text-xs text-gray-400">{meetingTarget} meeting · {missingTarget} missing of {total}</div>
  </div>);
}
