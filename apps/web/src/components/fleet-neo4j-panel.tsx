"use client";
export function FleetNeo4jPanel({ instances, available, nodes, relationships }: { instances: number; available: number; nodes: number; relationships: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔵 Neo4j</h3>
    <div className="text-sm">{available}/{instances} available · {nodes.toLocaleString()} nodes · {relationships.toLocaleString()} rels</div>
  </div>);
}
