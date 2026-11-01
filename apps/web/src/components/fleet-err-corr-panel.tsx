"use client";
export function FleetErrCorrPanel({ totalErrors, servicesAffected, hotspot, cascading }: { totalErrors: number; servicesAffected: number; hotspot: string | null; cascading: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 Error Correlation</h3>
    <div className="text-sm">{totalErrors} errors · {servicesAffected} services</div>
    {hotspot && <div className="text-xs text-blue-500">Hotspot: {hotspot}</div>}
    {cascading && <span className="text-xs text-red-500">🚨 Cascading failure</span>}
  </div>);
}
