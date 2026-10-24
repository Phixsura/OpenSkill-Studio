"use client";

interface TrafficAnalyzerPanelProps { totalRequests: number; avgLatencyMs: number;
  errorPct: number; topPath: string | null; topPathCount: number;
  byMethod: Record<string, number>; byStatus: Record<string, number>; }

export function TrafficAnalyzerPanel({ totalRequests, avgLatencyMs, errorPct, topPath, topPathCount, byMethod, byStatus }: TrafficAnalyzerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Traffic Analysis</h3>
        <span className="text-xs text-gray-400">{totalRequests.toLocaleString()} requests · {avgLatencyMs}ms · {errorPct}% errors</span>
      </div>
      {topPath && (
        <div className="px-4 py-2 border-b dark:border-gray-700 text-xs text-blue-600">
          🏆 Top: {topPath} ({topPathCount}×)
        </div>
      )}
      <div className="grid grid-cols-2 divide-x dark:divide-gray-700 p-3 text-xs">
        <div>
          <div className="text-gray-400 mb-1">Methods</div>
          {Object.entries(byMethod).map(([m, c]) => (
            <div key={m} className="flex justify-between py-0.5"><span>{m}</span><span className="text-gray-400">{c}</span></div>
          ))}
        </div>
        <div className="pl-3">
          <div className="text-gray-400 mb-1">Status Codes</div>
          {Object.entries(byStatus).map(([s, c]) => (
            <div key={s} className="flex justify-between py-0.5">
              <span className={s.startsWith("5") ? "text-red-500" : ""}>{s}</span>
              <span className="text-gray-400">{c}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
