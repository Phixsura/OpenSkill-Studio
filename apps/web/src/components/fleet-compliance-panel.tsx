"use client";
const GC: Record<string, string> = { A: "text-green-600", B: "text-blue-500", F: "text-red-500" };
export function FleetCompliancePanel({ score, grade, passing, failing }: { score: number; grade: string; passing: number; failing: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4 text-center">
    <h3 className="font-semibold mb-1">✅ Compliance</h3>
    <div className={`text-2xl font-black ${GC[grade] ?? ""}`}>{score}% — {grade}</div>
    <div className="text-xs text-gray-400">{passing} pass · {failing} fail</div>
  </div>);
}
