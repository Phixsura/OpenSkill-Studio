"use client";
export function FleetLoadBalancerV9Panel({ pools, connections }: { pools: number; connections: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ Load Balancer v9</h3>
    <div className="text-sm">{pools} pools · {connections.toLocaleString()} connections</div>
  </div>);
}
