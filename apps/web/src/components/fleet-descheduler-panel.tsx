"use client";
export function FleetDeschedulerPanel({ totalActions, podsEvicted, rebalances }: { totalActions: number; podsEvicted: number; rebalances: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Descheduler</h3>
    <div className="text-sm">{totalActions} actions · {podsEvicted} evicted · {rebalances} rebalances</div>
  </div>);
}
