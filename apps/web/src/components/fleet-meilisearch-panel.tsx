"use client";
export function FleetMeilisearchPanel({ instances, healthy, indexes, documents, searchP50 }: { instances: number; healthy: number; indexes: number; documents: number; searchP50: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔎 Meilisearch</h3>
    <div className="text-sm">{healthy}/{instances} healthy · {indexes} indexes · {documents.toLocaleString()} docs · {searchP50}ms</div>
  </div>);
}
