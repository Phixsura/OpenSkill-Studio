"use client";
export function FleetRlConfigPanel({ total, protected: prot, unprotected, fullyCovered }: { total: number; protected: number; unprotected: number; fullyCovered: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚦 Rate Limits</h3>
    {fullyCovered ? <span className="text-xs text-green-600">✅ All {total} endpoints protected</span>
     : <span className="text-xs text-yellow-600">⚠️ {unprotected} endpoints unprotected</span>}
  </div>);
}
