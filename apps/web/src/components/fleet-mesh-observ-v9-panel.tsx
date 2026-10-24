"use client";
export function FleetMeshObservV9Panel({ proxies, rps }: { proxies: number; rps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🕸️ Mesh Observability v9</h3>
    <div className="text-sm">{proxies} proxies · {rps.toLocaleString()} rps</div>
  </div>);
}
