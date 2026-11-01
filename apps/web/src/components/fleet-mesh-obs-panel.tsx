"use client";
export function FleetMeshObsPanel({ total, fullObs, coveragePct }: { total: number; fullObs: number; coveragePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👁️ Mesh Observability</h3>
    <div className={`text-lg font-bold ${coveragePct >= 80 ? "text-green-600" : "text-yellow-600"}`}>{coveragePct}%</div>
    <div className="text-xs text-gray-400">{fullObs}/{total} fully observable</div>
  </div>);
}
