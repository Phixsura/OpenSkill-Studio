"use client";
export function FleetAdaptConcPanel({ services, avgLimit, recentlyAdjusted, stable }: { services: number; avgLimit: number; recentlyAdjusted: number; stable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Adaptive Concurrency</h3>
    <div className="text-sm">avg limit {avgLimit} · {services} services</div>
    {!stable && <span className="text-xs text-blue-500">🔄 {recentlyAdjusted} recently adjusted</span>}
  </div>);
}
