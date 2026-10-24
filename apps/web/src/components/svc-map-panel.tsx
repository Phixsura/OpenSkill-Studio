"use client";
interface MapEdge { source: string; destination: string; requests: number; avgLatencyMs: number; errorRate: number; }
interface SvcMapPanelProps { nodes: string[]; edges: MapEdge[]; entryPoints: string[]; leafNodes: string[]; }
export function SvcMapPanel({ nodes, edges, entryPoints, leafNodes }: SvcMapPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗺️ Service Map</h3>
        <span className="text-xs text-gray-400">{nodes.length} nodes · {edges.length} edges</span>
      </div>
      <div className="p-3 flex gap-2 text-[10px]">
        <span className="text-gray-400">Entry: {entryPoints.join(", ")}</span>
        <span className="text-gray-400">Leaf: {leafNodes.join(", ")}</span>
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {edges.map(e => (
          <div key={`${e.source}→${e.destination}`} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{e.source} → {e.destination}</span>
            <span className={`text-gray-400 ${e.errorRate > 5 ? "text-red-500" : ""}`}>
              {e.requests.toLocaleString()} reqs · {e.avgLatencyMs}ms · {e.errorRate}% err
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
