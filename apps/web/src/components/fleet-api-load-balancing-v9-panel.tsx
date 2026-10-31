"use client";
export function FleetApiLoadBalancingV9Panel({ lbs, rps }: { lbs: number; rps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ API Load Balancing v9</h3>
    <div className="text-sm">{lbs} LBs · {rps.toLocaleString()} rps</div>
  </div>);
}
