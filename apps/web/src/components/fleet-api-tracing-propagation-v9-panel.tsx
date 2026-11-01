"use client";
export function FleetApiTracingPropagationV9Panel({ services, propagating }: { services: number; propagating: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 Trace Propagation v9</h3>
    <div className="text-sm">{services} services · {propagating} propagating</div>
  </div>);
}
