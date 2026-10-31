"use client";
export function FleetApiCachePolicyV9Panel({ policies, ttl }: { policies: number; ttl: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Cache Policy v9</h3>
    <div className="text-sm">{policies} policies · {ttl}s avg TTL</div>
  </div>);
}
