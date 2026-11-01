"use client";
export function FleetOpensearchPanel({ clusters, green, documents, shards }: { clusters: number; green: number; documents: number; shards: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 OpenSearch</h3>
    <div className="text-sm">{green}/{clusters} green · {documents.toLocaleString()} docs · {shards} shards</div>
  </div>);
}
