"use client";

interface DepGraphViewerProps { phases: string[][]; hasCycle: boolean;
  cycleNodes: string[]; nodeCount: number; edgeCount: number; }

export function DepGraphViewer({ phases, hasCycle, cycleNodes, nodeCount, edgeCount }: DepGraphViewerProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🔗 Dependency Graph</h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{nodeCount} nodes · {edgeCount} edges</span>
          {hasCycle && <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700">⚠️ Cycle</span>}
        </div>
      </div>
      {hasCycle ? (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg text-sm text-red-700 dark:text-red-400">
          Circular dependency detected: {cycleNodes.join(" ↔ ")}
        </div>
      ) : (
        <div className="space-y-3">
          {phases.map((phase, i) => (
            <div key={i}>
              <p className="text-xs font-semibold text-gray-400 mb-1">Phase {i + 1}</p>
              <div className="flex gap-2 flex-wrap">
                {phase.map(n => (
                  <span key={n} className="text-sm px-3 py-1.5 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded-lg font-mono">{n}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
