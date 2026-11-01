"use client";
export function FleetDatadogPanel({ total, active, monitors, alertsFiring }: { total: number; active: number; monitors: number; alertsFiring: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐶 Datadog</h3>
    <div className="text-sm">{active}/{total} active · {monitors} monitors</div>
    {alertsFiring > 0 && <span className="text-xs text-red-500">🔔 {alertsFiring} alerts firing</span>}
  </div>);
}
