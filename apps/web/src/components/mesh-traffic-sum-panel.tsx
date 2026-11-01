"use client";
interface TopFlow { source: string; destination: string; rps: number; }
interface MeshTrafficSumPanelProps { totalRps: number; totalRequests: number; errorRatePct: number;
  uniqueFlows: number; byProtocol: Record<string, number>; topFlows: TopFlow[]; }
export function MeshTrafficSumPanel({ totalRps, totalRequests, errorRatePct, uniqueFlows, byProtocol, topFlows }: MeshTrafficSumPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🕸️ Mesh Traffic Summary</h3>
        <span className="text-xs text-gray-400">{totalRps.toLocaleString()} rps · {uniqueFlows} flows · {errorRatePct}% err</span>
      </div>
      <div className="flex gap-2 p-3 text-xs">
        {Object.entries(byProtocol).map(([p, c]) => (
          <span key={p} className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800">{p}: {c.toLocaleString()}</span>
        ))}
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {topFlows.map(f => (
          <div key={`${f.source}→${f.destination}`} className="flex justify-between px-4 py-1 text-xs">
            <span className="font-mono">{f.source} → {f.destination}</span>
            <span className="text-gray-400">{f.rps.toLocaleString()} rps</span>
          </div>
        ))}
      </div>
    </div>
  );
}
