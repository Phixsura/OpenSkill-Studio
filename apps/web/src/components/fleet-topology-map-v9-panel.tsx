"use client";
export function FleetTopologyMapV9Panel({ nodes, connections }: { nodes: number; connections: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗺️ Topology Map v9</h3>
    <div className="text-sm">{nodes} nodes · {connections} connections</div>
  </div>);
}
