"use client";
export function FleetApiOpentelemetryV9Panel({ services, instrumented }: { services: number; instrumented: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 API OTel v9</h3>
    <div className="text-sm">{services} services · {instrumented} instrumented</div>
  </div>);
}
