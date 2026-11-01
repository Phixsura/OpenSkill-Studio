"use client";
export function FleetReadinessPanel({ ready, notReady, allReady }: { ready: number; notReady: number; allReady: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ Fleet Readiness</h3>
    <span className={`text-xs ${allReady ? "text-green-600" : "text-yellow-600"}`}>
      {ready} ready · {notReady} not ready
    </span>
  </div>);
}
