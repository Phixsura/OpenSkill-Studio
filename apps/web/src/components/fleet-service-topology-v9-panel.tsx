"use client";
export function FleetServiceTopologyV9Panel({ nodes, edges }: { nodes: number; edges: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗺️ Service Topology v9</h3>
    <div className="text-sm">{nodes} nodes · {edges} edges</div>
  </div>);
}
