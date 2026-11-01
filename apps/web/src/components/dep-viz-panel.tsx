"use client";
interface DepVizPanelProps { mermaid: string; nodes: number; edges: number;
  density: number; mostDependedOn: string; mostDependent: string; }
export function DepVizPanel({ mermaid, nodes, edges, density, mostDependedOn, mostDependent }: DepVizPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🕸️ Dependency Graph</h3>
        <span className="text-xs text-gray-400">{nodes} nodes · {edges} edges · density {density}</span>
      </div>
      <div className="p-4 text-xs space-y-1">
        <div className="text-gray-400">Most depended on: <span className="text-blue-500 font-bold">{mostDependedOn}</span></div>
        <div className="text-gray-400">Most dependent: <span className="text-yellow-600 font-bold">{mostDependent}</span></div>
      </div>
      <pre className="border-t dark:border-gray-700 p-3 text-[10px] text-gray-500 bg-gray-50 dark:bg-gray-900 overflow-x-auto">{mermaid}</pre>
    </div>
  );
}
