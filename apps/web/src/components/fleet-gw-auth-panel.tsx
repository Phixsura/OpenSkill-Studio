"use client";
export function FleetGwAuthPanel({ total, noAuth, secure }: { total: number; noAuth: number; secure: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 Gateway Auth</h3>
    {secure ? <span className="text-xs text-green-600">✅ All {total} endpoints authenticated</span>
     : <span className="text-xs text-red-500">⚠️ {noAuth} endpoints without auth</span>}
  </div>);
}
