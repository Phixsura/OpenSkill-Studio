"use client";
interface FlowNode { id: string; label: string; operation: string; durationMs: number; }
interface ReqFlowVizPanelProps { nodes: FlowNode[]; totalMs: number; bottleneck: string; }
export function ReqFlowVizPanel({ nodes, totalMs, bottleneck }: ReqFlowVizPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔀 Request Flow</h3>
        <span className="text-xs text-gray-400">{totalMs}ms total · bottleneck: {bottleneck}</span>
      </div>
      <div className="p-4 flex items-center gap-1">
        {nodes.map((n, i) => (
          <div key={n.id} className="flex items-center gap-1">
            <div className={`px-2 py-1.5 rounded text-xs border ${n.label === bottleneck ? "border-red-400 bg-red-50 dark:bg-red-950" : "border-gray-300 dark:border-gray-600"}`}>
              <div className="font-semibold">{n.label}</div>
              <div className="text-[10px] text-gray-400">{n.operation} · {n.durationMs}ms</div>
            </div>
            {i < nodes.length - 1 && <span className="text-gray-400">→</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
