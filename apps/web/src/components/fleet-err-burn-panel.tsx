"use client";
export function FleetErrBurnPanel({ total, fastBurn, slowBurn, alert }: { total: number; fastBurn: number; slowBurn: number; alert: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔥 Error Budget Burn</h3>
    <div className="text-sm">{fastBurn} fast · {slowBurn} slow burn</div>
    {alert && <span className="text-xs text-red-500">🚨 Fast burn detected!</span>}
  </div>);
}
