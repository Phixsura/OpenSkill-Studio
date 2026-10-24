"use client";
export function FleetReadyGatePanel({ total, passed, blocked, allClear }: { total: number; passed: number; blocked: number; allClear: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚧 Readiness Gates</h3>
    {allClear ? <span className="text-xs text-green-600">✅ All {total} gates clear</span>
     : <span className="text-xs text-yellow-600">⚠️ {blocked} blocked</span>}
  </div>);
}
