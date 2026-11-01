"use client";
export function FleetGracefulPanel({ total, graceful, forcedKill, compliant }: { total: number; graceful: number; forcedKill: number; compliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛑 Graceful Shutdown</h3>
    {compliant ? <span className="text-xs text-green-600">✅ All {total} pods shutdown gracefully</span>
     : <span className="text-xs text-yellow-600">⚠️ {forcedKill} forced kills</span>}
  </div>);
}
