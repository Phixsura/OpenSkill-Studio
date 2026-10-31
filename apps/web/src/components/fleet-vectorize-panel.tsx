"use client";
export function FleetVectorizePanel({ indexes, active, vectors, queries }: { indexes: number; active: number; vectors: number; queries: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔮 Vectorize</h3>
    <div className="text-sm">{active}/{indexes} active · {vectors.toLocaleString()} vectors · {queries.toLocaleString()} queries</div>
  </div>);
}
