"use client";

interface MeshPair { source: string; destination: string; count: number; avgMs: number; errorRate: number; }
interface MeshObservDashProps { pairs: MeshPair[]; totalFlows: number; totalErrors: number; }

export function MeshObservDash({ pairs, totalFlows, totalErrors }: MeshObservDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🕸️ Mesh Traffic</h3>
        <span className="text-xs text-gray-400">{totalFlows.toLocaleString()} flows · {totalErrors} errors</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {pairs.map(p => (
          <div key={`${p.source}→${p.destination}`} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{p.source} → {p.destination}</span>
            <div className="flex items-center gap-2 text-gray-400">
              <span>{p.count.toLocaleString()}</span>
              <span>{p.avgMs}ms</span>
              <span className={p.errorRate > 5 ? "text-red-500" : ""}>{p.errorRate}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
