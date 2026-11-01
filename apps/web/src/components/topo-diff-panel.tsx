"use client";
interface TopoDiffPanelProps { addedNodes: string[]; removedNodes: string[];
  addedEdges: string[]; removedEdges: string[]; risk: string; totalChanges: number; }
const RISK_STYLE: Record<string, string> = { high: "text-red-600", medium: "text-yellow-600", low: "text-green-600", none: "text-gray-400" };
export function TopoDiffPanel({ addedNodes, removedNodes, addedEdges, removedEdges, risk, totalChanges }: TopoDiffPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔀 Topology Diff</h3>
        <span className={`text-xs font-bold ${RISK_STYLE[risk] ?? ""}`}>{risk} risk · {totalChanges} changes</span>
      </div>
      <div className="p-4 text-xs font-mono space-y-0.5">
        {addedNodes.map(n => <div key={n} className="text-green-600">+ node: {n}</div>)}
        {removedNodes.map(n => <div key={n} className="text-red-600">- node: {n}</div>)}
        {addedEdges.map(e => <div key={e} className="text-green-600">+ edge: {e}</div>)}
        {removedEdges.map(e => <div key={e} className="text-red-600">- edge: {e}</div>)}
        {totalChanges === 0 && <div className="text-gray-400">No changes</div>}
      </div>
    </div>
  );
}
