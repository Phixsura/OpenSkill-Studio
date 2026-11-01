"use client";

interface SummaryInfo {
  total_requests_7d: number; total_requests_30d: number; unique_consumers_7d: number;
  avg_latency_ms: number; p99_latency_ms: number; error_rate_pct: number;
  request_growth_pct: number; consumer_growth_pct: number;
  top_endpoint: string; top_consumer: string;
  webhook_delivery_rate_pct: number; health_indicator: string;
}
interface Props { summary: SummaryInfo; appName: string; }

const hColor: Record<string, string> = { excellent: "text-green-600", good: "text-blue-600", fair: "text-yellow-600", poor: "text-red-600" };

export default function APIDeveloperAPIApiPlatformAnalyticsSummaryCard({ summary: s, appName }: Props) {
  return (
    <div className="rounded-xl border-2 border-blue-200 bg-white p-5 shadow-lg dark:border-blue-800 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">📊 Platform Analytics</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-black ${hColor[s.health_indicator] ?? ""}`}>{s.health_indicator.toUpperCase()}</span>
      </div>
      <div className="grid grid-cols-4 gap-1.5 text-center">
        {[
          { l: "7d Requests", v: s.total_requests_7d.toLocaleString() },
          { l: "30d Requests", v: s.total_requests_30d.toLocaleString() },
          { l: "Consumers", v: s.unique_consumers_7d },
          { l: "Avg Latency", v: `${s.avg_latency_ms}ms` },
          { l: "p99", v: `${s.p99_latency_ms}ms` },
          { l: "Error Rate", v: `${s.error_rate_pct}%` },
          { l: "Req Growth", v: `${s.request_growth_pct > 0 ? "+" : ""}${s.request_growth_pct}%` },
          { l: "User Growth", v: `${s.consumer_growth_pct > 0 ? "+" : ""}${s.consumer_growth_pct}%` },
          { l: "Top Endpoint", v: s.top_endpoint || "—" },
          { l: "Top Consumer", v: s.top_consumer || "—" },
          { l: "Webhook Rate", v: `${s.webhook_delivery_rate_pct}%` },
          { l: "Health", v: s.health_indicator },
        ].map((m) => (
          <div key={m.l} className="rounded bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-[10px] font-bold text-gray-900 dark:text-gray-100 truncate px-1">{m.v}</p>
            <p className="text-[7px] text-gray-400">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
