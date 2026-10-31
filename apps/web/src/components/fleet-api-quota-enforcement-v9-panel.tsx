"use client";
export function FleetApiQuotaEnforcementV9Panel({ consumers, exceeded }: { consumers: number; exceeded: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📏 Quota Enforcement v9</h3>
    <div className="text-sm">{consumers} consumers · {exceeded} exceeded</div>
  </div>);
}
