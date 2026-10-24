"use client";
export function FleetApiDependencyCheckV9Panel({ deps, healthy }: { deps: number; healthy: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 API Dep Check v9</h3>
    <div className="text-sm">{deps} deps · {healthy} healthy</div>
  </div>);
}
