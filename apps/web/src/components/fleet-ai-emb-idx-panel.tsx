"use client";
export function FleetAiEmbIdxPanel({ indexes, active, vectors, searches, avgMs }: { indexes: number; active: number; vectors: number; searches: number; avgMs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔢 Embedding Index</h3>
    <div className="text-sm">{active}/{indexes} active · {vectors.toLocaleString()} vectors · {searches.toLocaleString()} searches · {avgMs}ms</div>
  </div>);
}
