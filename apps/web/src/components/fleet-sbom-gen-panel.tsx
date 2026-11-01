"use client";
export function FleetSbomGenPanel({ total, withSbom, coveragePct, compliant }: { total: number; withSbom: number; coveragePct: number; compliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 SBOM</h3>
    <div className={`text-lg font-bold ${compliant ? "text-green-600" : "text-yellow-600"}`}>{coveragePct}%</div>
    <div className="text-xs text-gray-400">{withSbom}/{total} with SBOM</div>
  </div>);
}
