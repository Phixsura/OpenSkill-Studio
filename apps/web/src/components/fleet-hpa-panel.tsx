"use client";
export function FleetHpaPanel({ total, atMax, atMin, scalingPressure }: { total: number; atMax: number; atMin: number; scalingPressure: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Fleet HPA</h3>
    <div className="text-sm">{total} HPAs · {atMax} at max · {atMin} at min</div>
    {scalingPressure && <span className="text-xs text-yellow-600">⚠️ Scaling pressure</span>}
  </div>);
}
