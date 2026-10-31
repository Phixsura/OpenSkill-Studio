"use client";
export function FleetCrdManagerV9Panel({ crds, instances }: { crds: number; instances: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ CRD Manager v9</h3>
    <div className="text-sm">{crds} CRDs · {instances} instances</div>
  </div>);
}
