"use client";
const GC: Record<string, string> = { A: "text-green-600", B: "text-blue-500", C: "text-yellow-600", F: "text-red-500" };
export function FleetSecPosturePanel({ score, grade, criticalFails }: { score: number; grade: string; criticalFails: number; }) {
  return (<div className="rounded-2xl border-2 dark:border-gray-600 p-6 text-center">
    <h3 className="font-semibold mb-2">🛡️ Security Posture</h3>
    <div className={`text-3xl font-black ${GC[grade] ?? ""}`}>{score}% — {grade}</div>
    {criticalFails > 0 && <div className="text-xs text-red-500 mt-1">🚨 {criticalFails} critical failures</div>}
  </div>);
}
