"use client";
export function FleetHaystackPanel({ pipelines, active, nodes, queries }: { pipelines: number; active: number; nodes: number; queries: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌾 Haystack</h3>
    <div className="text-sm">{active}/{pipelines} active · {nodes} nodes · {queries.toLocaleString()} queries</div>
  </div>);
}
