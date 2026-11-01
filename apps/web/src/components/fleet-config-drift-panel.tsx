"use client";
export function FleetConfigDriftPanel({ drifted, total, consistent }: { drifted: number; total: number; consistent: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚙️ Config Drift</h3>
    {consistent ? <span className="text-xs text-green-600">✅ All {total} instances consistent</span>
     : <span className="text-xs text-yellow-600">⚠️ {drifted}/{total} drifted</span>}
  </div>);
}
