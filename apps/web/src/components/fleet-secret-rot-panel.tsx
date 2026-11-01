"use client";
export function FleetSecretRotPanel({ total, stale, compliant }: { total: number; stale: number; compliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 Secret Rotation</h3>
    {compliant ? <span className="text-xs text-green-600">✅ All {total} secrets fresh</span>
     : <span className="text-xs text-yellow-600">⚠️ {stale} stale secrets {">"} 90 days</span>}
  </div>);
}
