"use client";
export function FleetAiEmbIndexPanel({ indexes, active, vectors, dims, searches, p99 }: { indexes: number; active: number; vectors: number; dims: number; searches: number; p99: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧬 AI Embedding Index</h3>
    <div className="text-sm">{active}/{indexes} active · {vectors.toLocaleString()} vectors · {dims}d · {searches.toLocaleString()} searches · p99 {p99}ms</div>
  </div>);
}
