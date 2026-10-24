"use client";
export function FleetTypesensePanel({ nodes, healthy, collections, documents }: { nodes: number; healthy: number; collections: number; documents: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔤 Typesense</h3>
    <div className="text-sm">{healthy}/{nodes} healthy · {collections} collections · {documents.toLocaleString()} docs</div>
  </div>);
}
