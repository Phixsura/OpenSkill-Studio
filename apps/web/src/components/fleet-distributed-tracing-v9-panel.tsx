"use client";
export function FleetDistributedTracingV9Panel({ services, sps }: { services: number; sps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 Distributed Tracing v9</h3>
    <div className="text-sm">{services} services · {sps.toLocaleString()} spans/s</div>
  </div>);
}
