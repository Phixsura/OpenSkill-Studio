"use client";
interface Consumer { consumerId: string; requests: number; avgLatencyMs: number; errorRatePct: number; }
interface ConsumerAnalyticsPanelProps { consumers: Consumer[]; totalConsumers: number; totalRequests: number; }
export function ConsumerAnalyticsPanel({ consumers, totalConsumers, totalRequests }: ConsumerAnalyticsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">👥 Consumer Analytics</h3>
        <span className="text-xs text-gray-400">{totalConsumers} consumers · {totalRequests.toLocaleString()} reqs</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {consumers.map(c => (
          <div key={c.consumerId} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{c.consumerId}</span>
            <span className="text-gray-400">{c.requests.toLocaleString()} reqs · {c.avgLatencyMs}ms · {c.errorRatePct}% err</span>
          </div>
        ))}
      </div>
    </div>
  );
}
