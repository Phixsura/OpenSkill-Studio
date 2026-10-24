"use client";
export function FleetMtlsPanel({ total, mtlsEnabled, pct, fullCoverage }: { total: number; mtlsEnabled: number; pct: number; fullCoverage: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 mTLS Coverage</h3>
    <div className={`text-lg font-bold ${fullCoverage ? "text-green-600" : "text-yellow-600"}`}>{pct}%</div>
    <div className="text-xs text-gray-400">{mtlsEnabled}/{total} services</div>
  </div>);
}
