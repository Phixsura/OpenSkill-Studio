"use client";
export function FleetAiFeatStorePanel({ stores, active, features, qps, freshness }: { stores: number; active: number; features: number; qps: number; freshness: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗄️ AI Feature Store</h3>
    <div className="text-sm">{active}/{stores} active · {features.toLocaleString()} features · {qps.toLocaleString()} QPS · {freshness}ms</div>
  </div>);
}
