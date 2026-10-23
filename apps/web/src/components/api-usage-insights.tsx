"use client";

interface ApiUsageInsightsProps { totalRequests: number; avgLatencyMs: number;
  errorRatePct: number; topEndpoint: string | null;
  byMethod: Record<string, number>; byStatus: Record<string, number>; }

export function ApiUsageInsights({ totalRequests, avgLatencyMs, errorRatePct, topEndpoint, byMethod, byStatus }: ApiUsageInsightsProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 API Usage</h3>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {[{ l: "Requests", v: totalRequests.toLocaleString() },
          { l: "Avg Latency", v: `${avgLatencyMs}ms` },
          { l: "Error Rate", v: `${errorRatePct}%` },
          { l: "Top", v: topEndpoint ?? "—" }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-2 divide-x dark:divide-gray-700 p-3 text-xs">
        <div>
          <div className="text-gray-400 mb-1">By Method</div>
          {Object.entries(byMethod).map(([m, c]) => (
            <div key={m} className="flex justify-between py-0.5"><span>{m}</span><span className="text-gray-400">{c}</span></div>
          ))}
        </div>
        <div className="pl-3">
          <div className="text-gray-400 mb-1">By Status</div>
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
