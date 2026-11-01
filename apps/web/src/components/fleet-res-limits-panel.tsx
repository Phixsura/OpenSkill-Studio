"use client";
export function FleetResLimitsPanel({ total, noCpu, noMem, allLimited }: { total: number; noCpu: number; noMem: number; allLimited: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📏 Resource Limits</h3>
    {allLimited ? <span className="text-xs text-green-600">✅ All {total} containers have limits</span>
     : <span className="text-xs text-yellow-600">⚠️ {noCpu} no CPU · {noMem} no memory limits</span>}
  </div>);
}
