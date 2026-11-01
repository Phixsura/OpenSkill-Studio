"use client";

interface GraphNode { id: string; label: string; type: string; inDegree: number; outDegree: number; isRoot: boolean; isLeaf: boolean; }
interface NetworkGraphViewProps { nodes: GraphNode[]; nodeCount: number; edgeCount: number; rootCount: number; leafCount: number; }

const typeIcons: Record<string, string> = {
  service: "⚙️", database: "🗃️", gateway: "🌐", cache: "💾", queue: "📨",
};

export function NetworkGraphView({ nodes, nodeCount, edgeCount, rootCount, leafCount }: NetworkGraphViewProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Service Graph</h3>
        <div className="flex gap-2 text-xs text-gray-400">
          <span>{nodeCount} nodes</span>
          <span>{edgeCount} edges</span>
        </div>
      </div>
      <div className="flex gap-3 text-xs">
        <span className="text-blue-600">{rootCount} entry points</span>
        <span className="text-green-600">{leafCount} leaf services</span>
      </div>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {nodes.map(n => (
          <div key={n.id} className={`rounded-lg border p-3 dark:border-gray-700 ${n.isRoot ? "border-blue-400" : n.isLeaf ? "border-green-400" : ""}`}>
            <div className="flex items-center gap-2">
              <span>{typeIcons[n.type] ?? "⚙️"}</span>
              <span className="text-sm font-medium">{n.label}</span>
            </div>
            <p className="mt-1 text-xs text-gray-400">{n.inDegree}↓ {n.outDegree}↑</p>
          </div>
        ))}
      </div>
    </div>
  );
}
