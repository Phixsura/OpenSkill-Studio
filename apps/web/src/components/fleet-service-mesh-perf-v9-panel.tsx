"use client";
export function FleetServiceMeshPerfV9Panel({ proxies, overhead }: { proxies: number; overhead: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🕸️ Mesh Perf v9</h3>
    <div className="text-sm">{proxies} proxies · {overhead}ms overhead</div>
  </div>);
}
