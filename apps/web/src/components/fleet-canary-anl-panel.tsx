"use client";
const VC: Record<string, string> = { promote: "text-green-600", hold: "text-yellow-600", rollback: "text-red-500" };
export function FleetCanaryAnlPanel({ errorDelta, latencyDelta, score, verdict }: { errorDelta: number; latencyDelta: number; score: number; verdict: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐦 Canary Analysis</h3>
    <div className={`text-lg font-bold ${VC[verdict] ?? ""}`}>{verdict.toUpperCase()} ({score})</div>
    <div className="text-xs text-gray-400">Δerr {errorDelta}% · Δlat {latencyDelta}%</div>
  </div>);
}
