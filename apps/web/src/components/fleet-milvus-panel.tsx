"use client";
export function FleetMilvusPanel({ nodes, healthy, entities, searchQps }: { nodes: number; healthy: number; entities: number; searchQps: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔮 Milvus</h3>
    <div className="text-sm">{healthy}/{nodes} healthy · {entities.toLocaleString()} entities · {searchQps.toLocaleString()} qps</div>
  </div>);
}
