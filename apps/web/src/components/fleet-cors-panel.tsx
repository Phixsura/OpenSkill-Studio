"use client";
export function FleetCorsPanel({ total, wildcardOrigin, secure }: { total: number; wildcardOrigin: number; secure: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 CORS Policy</h3>
    {secure ? <span className="text-xs text-green-600">✅ All {total} services secure</span>
     : <span className="text-xs text-red-500">⚠️ {wildcardOrigin} with wildcard origin</span>}
  </div>);
}
