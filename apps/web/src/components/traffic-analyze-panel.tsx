"use client";
interface TopEndpoint { endpoint: string; count: number; }
interface TrafficAnalyzePanelProps { total: number; avgLatencyMs: number; errorRatePct: number;
  byMethod: Record<string, number>; topEndpoints: TopEndpoint[]; spikeDetected: boolean; }
export function TrafficAnalyzePanel({ total, avgLatencyMs, errorRatePct, byMethod, topEndpoints, spikeDetected }: TrafficAnalyzePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Traffic Analysis</h3>
        <span className={`text-xs font-bold ${spikeDetected ? "text-red-500" : "text-green-600"}`}>
          {total.toLocaleString()} reqs · {avgLatencyMs}ms avg · {errorRatePct}% err{spikeDetected ? " · ⚠ SPIKE" : ""}
        </span>
      </div>
      <div className="flex gap-2 p-3 text-xs">
        {Object.entries(byMethod).map(([m, c]) => (
          <span key={m} className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800">{m}: {c}</span>
        ))}
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {topEndpoints.map(ep => (
          <div key={ep.endpoint} className="flex justify-between px-4 py-1 text-xs">
            <span className="font-mono">{ep.endpoint}</span>
            <span className="text-gray-400">{ep.count.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
