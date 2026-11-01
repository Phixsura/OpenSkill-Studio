"use client";
export function FleetDepGraphPanel({ nodes, edges, roots, leaves }: { nodes: number; edges: number; roots: number; leaves: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🕸️ Dependency Graph</h3>
    <div className="text-sm">{nodes} nodes · {edges} edges · {roots} roots · {leaves} leaves</div>
  </div>);
}
