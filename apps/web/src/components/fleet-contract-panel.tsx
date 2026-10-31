"use client";
export function FleetContractPanel({ total, passing, broken, compatible }: { total: number; passing: number; broken: number; compatible: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 Contract Tests</h3>
    {compatible ? <span className="text-xs text-green-600">✅ All {total} contracts passing</span>
     : <span className="text-xs text-red-500">⚠️ {broken} broken contracts</span>}
  </div>);
}
