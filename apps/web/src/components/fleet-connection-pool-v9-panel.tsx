"use client";
export function FleetConnectionPoolV9Panel({ pools, active }: { pools: number; active: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 Connection Pool v9</h3>
    <div className="text-sm">{pools} pools · {active} active</div>
  </div>);
}
