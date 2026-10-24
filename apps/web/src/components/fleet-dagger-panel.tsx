"use client";
export function FleetDaggerPanel({ pipelines, cacheHits, operations, avgDuration }: { pipelines: number; cacheHits: number; operations: number; avgDuration: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗡️ Dagger</h3>
    <div className="text-sm">{pipelines} pipelines · {cacheHits} cache hits · {avgDuration}s avg</div>
  </div>);
}
