"use client";
export function FleetLoadShedPanel({ total, shedding, requestsShed, calm }: { total: number; shedding: number; requestsShed: number; calm: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Load Shedding</h3>
    {calm ? <span className="text-xs text-green-600">✅ No shedding</span>
     : <span className="text-xs text-yellow-600">⚠️ {shedding} services shedding ({requestsShed.toLocaleString()} shed)</span>}
  </div>);
}
