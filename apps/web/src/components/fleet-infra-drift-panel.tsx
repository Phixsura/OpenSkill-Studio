"use client";
export function FleetInfraDriftPanel({ total, drifted, unmanaged, clean }: { total: number; drifted: number; unmanaged: number; clean: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 IaC Drift</h3>
    {clean ? <span className="text-xs text-green-600">✅ All {total} resources in sync</span>
     : <span className="text-xs text-yellow-600">⚠️ {drifted} drifted · {unmanaged} unmanaged</span>}
  </div>);
}
