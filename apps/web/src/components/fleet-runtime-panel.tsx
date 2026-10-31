"use client";
export function FleetRuntimePanel({ total, heterogeneous }: { total: number; heterogeneous: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐳 Container Runtime</h3>
    <div className="text-sm">{total} nodes</div>
    {heterogeneous && <span className="text-xs text-yellow-600">⚠️ Mixed runtimes</span>}
  </div>);
}
