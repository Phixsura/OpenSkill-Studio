"use client";
export function FleetServiceDependencyV9Panel({ deps, circular }: { deps: number; circular: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 Service Dependency v9</h3>
    <div className="text-sm">{deps} deps · {circular} circular</div>
  </div>);
}
