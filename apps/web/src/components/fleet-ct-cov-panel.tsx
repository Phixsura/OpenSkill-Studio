"use client";
export function FleetCtCovPanel({ total, withTests, without, coveragePct, good }: { total: number; withTests: number; without: number; coveragePct: number; good: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 Contract Tests</h3>
    <div className={`text-lg font-bold ${good ? "text-green-600" : "text-yellow-600"}`}>{coveragePct}%</div>
    <div className="text-xs text-gray-400">{withTests}/{total} covered</div>
  </div>);
}
