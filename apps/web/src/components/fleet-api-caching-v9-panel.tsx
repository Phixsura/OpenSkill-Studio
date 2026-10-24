"use client";
export function FleetApiCachingV9Panel({ endpoints, hitRate }: { endpoints: number; hitRate: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ API Caching v9</h3>
    <div className="text-sm">{endpoints} endpoints · {hitRate}% hit rate</div>
  </div>);
}
