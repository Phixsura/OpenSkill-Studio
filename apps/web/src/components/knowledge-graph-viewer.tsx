"use client";

interface GraphNode { id: string; type: string; label: string; }
interface GraphEdge { from: string; to: string; type: string; }
interface KnowledgeGraphViewerProps { nodes: GraphNode[]; edges: GraphEdge[];
  nodeCount: number; edgeCount: number; entityTypes: string[]; }

const TYPE_COLORS: Record<string, string> = {
  service: "border-blue-400", database: "border-green-400", team: "border-purple-400",
  entity: "border-gray-400",
};

export function KnowledgeGraphViewer({ nodes, edges, nodeCount, edgeCount, entityTypes }: KnowledgeGraphViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🧠 Knowledge Graph</h3>
        <span className="text-xs text-gray-400">{nodeCount} nodes · {edgeCount} edges · {entityTypes.length} types</span>
      </div>
      <div className="grid grid-cols-3 sm:grid-cols-4 gap-2 p-3">
        {nodes.map(n => (
          <div key={n.id} className={`border-2 ${TYPE_COLORS[n.type] ?? TYPE_COLORS.entity} rounded-lg p-2 text-center`}>
            <div className="text-xs font-mono font-bold">{n.label}</div>
            <div className="text-[10px] text-gray-400">{n.type}</div>
          </div>
        ))}
      </div>
      <div className="p-3 border-t dark:border-gray-700 text-[10px] text-gray-400">
        {edges.map((e, i) => `${e.from} →${e.type}→ ${e.to}`).join(" · ")}
      </div>
    </div>
  );
}
