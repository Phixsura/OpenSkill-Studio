"use client";
export function FleetReadinessAssessPanel({ totalChecks, passed, blockers, score, launchReady }: { totalChecks: number; passed: number; blockers: number; score: number; launchReady: boolean; }) {
  return (<div className="rounded-2xl border-2 dark:border-gray-600 p-6 text-center">
    <h3 className="font-semibold mb-2">🚀 Launch Readiness</h3>
    <div className={`text-2xl font-black ${launchReady ? "text-green-600" : "text-red-500"}`}>{launchReady ? "READY" : "NOT READY"}</div>
    <div className="text-xs text-gray-400 mt-1">{passed}/{totalChecks} checks · {blockers} blockers · {score}%</div>
  </div>);
}
