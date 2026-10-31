"use client";
export function FleetApiObservabilityV9Panel({ apis, instrumented }: { apis: number; instrumented: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👁️ API Observability v9</h3>
    <div className="text-sm">{apis} APIs · {instrumented} instrumented</div>
  </div>);
}
