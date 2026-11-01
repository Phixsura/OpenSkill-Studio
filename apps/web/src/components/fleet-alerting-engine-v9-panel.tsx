"use client";
export function FleetAlertingEngineV9Panel({ total, firing }: { total: number; firing: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔔 Alerting Engine v9</h3>
    <div className="text-sm">{total} alerts · {firing} firing</div>
  </div>);
}
