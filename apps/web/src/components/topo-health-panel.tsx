"use client";
interface TopoHealthPanelProps { overall: string; nodes: number; healthyNodes: number;
  edges: number; healthyEdges: number; criticalPathIssues: number; nodeHealthPct: number; }
const OV_STYLE: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", critical: "bg-red-500" };
export function TopoHealthPanel({ overall, nodes, healthyNodes, edges, healthyEdges, criticalPathIssues, nodeHealthPct }: TopoHealthPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center text-sm font-bold ${OV_STYLE[overall] ?? "bg-gray-500"}`}>
        Topology: {overall.toUpperCase()} · {nodeHealthPct}% nodes healthy
      </div>
      <div className="grid grid-cols-4 gap-2 p-4 text-center text-xs">
        <div><span className="text-gray-400">Nodes</span><div className="font-bold">{healthyNodes}/{nodes}</div></div>
        <div><span className="text-gray-400">Edges</span><div className="font-bold">{healthyEdges}/{edges}</div></div>
        <div><span className="text-gray-400">Critical</span><div className={`font-bold ${criticalPathIssues > 0 ? "text-red-500" : ""}`}>{criticalPathIssues}</div></div>
        <div><span className="text-gray-400">Health</span><div className="font-bold">{nodeHealthPct}%</div></div>
      </div>
    </div>
  );
}
