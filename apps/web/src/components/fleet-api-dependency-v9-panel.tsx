"use client";
export function FleetApiDependencyV9Panel({ apis, circular }: { apis: number; circular: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔗 API Dependency v9</h3>
    <div className="text-sm">{apis} APIs · {circular} circular</div>
  </div>);
}
