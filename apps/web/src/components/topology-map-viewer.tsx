"use client";

interface TopoNode { name: string; layer: string; healthy: boolean; }
interface TopoEdge { from: string; to: string; protocol: string; }
interface TopologyMapViewerProps { nodes: TopoNode[]; edges: TopoEdge[];
  layers: Record<string, string[]>; healthy: number; nodeCount: number; }

export function TopologyMapViewer({ nodes, edges, layers, healthy, nodeCount }: TopologyMapViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗺️ Service Topology</h3>
        <span className="text-xs text-gray-400">{nodeCount} nodes · {edges.length} edges · {healthy} healthy</span>
      </div>
      {Object.entries(layers).map(([layer, svcs]) => (
        <div key={layer} className="border-b last:border-0 dark:border-gray-700 p-3">
          <div className="text-[10px] text-gray-400 mb-1 uppercase">{layer}</div>
          <div className="flex gap-2 flex-wrap">
            {svcs.map(s => {
              const node = nodes.find(n => n.name === s);
              return (
                <span key={s} className={`px-2 py-1 text-xs rounded-lg border ${node?.healthy ? "border-green-300 dark:border-green-800" : "border-red-300 dark:border-red-800"}`}>
                  {node?.healthy ? "🟢" : "🔴"} {s}
                </span>
              );
            })}
          </div>
        </div>
      ))}
      <div className="p-3 bg-gray-50 dark:bg-gray-800/50 text-[10px] text-gray-400">
        Connections: {edges.map(e => `${e.from}→${e.to}`).join(", ")}
      </div>
    </div>
  );
}
