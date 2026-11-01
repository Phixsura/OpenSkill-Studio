"use client";
export function FleetWeaviatePanel({ nodes, healthy, objects, vectors }: { nodes: number; healthy: number; objects: number; vectors: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔮 Weaviate</h3>
    <div className="text-sm">{healthy}/{nodes} healthy · {objects.toLocaleString()} objects · {vectors.toLocaleString()} vectors</div>
  </div>);
}
